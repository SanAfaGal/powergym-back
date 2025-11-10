"""
Statistics Service

Business logic for admin dashboard statistics.
Aggregates data from multiple sources efficiently.
"""

from datetime import datetime, date, timedelta, timezone
from decimal import Decimal
from typing import Dict, List, Optional
from calendar import monthrange

from sqlalchemy import func, and_, distinct, extract
from sqlalchemy.orm import Session, joinedload

from app.db.models import (
    ClientModel,
    SubscriptionModel,
    PaymentModel,
    AttendanceModel,
    ProductModel,
    InventoryMovementModel,
    SubscriptionStatusEnum,
    PaymentMethodEnum,
    InventoryMovementTypeEnum,
)
from app.schemas.statistics import (
    PeriodInfo,
    ClientStats,
    SubscriptionStats,
    FinancialStats,
    AttendanceStats,
    InventoryStats,
    RecentActivity,
    Alert,
    RevenueByMethod,
    SalesInfo,
    StatisticsResponse,
    ActivityMetadata,
)
from app.utils.timezone import TIMEZONE, get_date_range_utc


class StatisticsService:
    """Service for aggregating dashboard statistics."""

    def __init__(self, db: Session):
        self.db = db

    def calculate_period_dates(self, period: str, ref_date: date) -> Dict[str, date]:
        """
        Calculate start and end dates for the period.

        Args:
            period: Type of period ('today', 'week', 'month', 'year')
            ref_date: Reference date for calculation

        Returns:
            Dictionary with 'start' and 'end' dates
        """
        if period == "today":
            return {"start": ref_date, "end": ref_date}
        elif period == "week":
            # Week containing ref_date (Monday to Sunday)
            days_since_monday = ref_date.weekday()
            start = ref_date - timedelta(days=days_since_monday)
            return {"start": start, "end": start + timedelta(days=6)}
        elif period == "month":
            start = ref_date.replace(day=1)
            last_day = monthrange(ref_date.year, ref_date.month)[1]
            end = ref_date.replace(day=last_day)
            return {"start": start, "end": end}
        elif period == "year":
            start = date(ref_date.year, 1, 1)
            end = date(ref_date.year, 12, 31)
            return {"start": start, "end": end}
        else:
            raise ValueError(f"Invalid period: {period}")

    def get_client_stats(self, period_dates: Dict[str, date]) -> ClientStats:
        """Get client statistics filtered by date range."""
        period_start = datetime.combine(period_dates["start"], datetime.min.time())
        period_end = datetime.combine(period_dates["end"], datetime.max.time())
        period_start_utc, _ = get_date_range_utc(period_start)
        _, period_end_utc = get_date_range_utc(period_end)

        # Total, active, inactive
        total = self.db.query(func.count(ClientModel.id)).scalar() or 0
        active = (
            self.db.query(func.count(ClientModel.id))
            .filter(ClientModel.is_active == True)
            .scalar()
            or 0
        )
        inactive = total - active

        # New clients within the period
        new_in_period = (
            self.db.query(func.count(ClientModel.id))
            .filter(
                and_(
                    ClientModel.created_at >= period_start_utc,
                    ClientModel.created_at <= period_end_utc,
                )
            )
            .scalar()
            or 0
        )

        # Clients with active subscriptions
        with_active_subscription = (
            self.db.query(func.count(func.distinct(ClientModel.id)))
            .join(SubscriptionModel, ClientModel.id == SubscriptionModel.client_id)
            .filter(
                and_(
                    SubscriptionModel.status == SubscriptionStatusEnum.ACTIVE,
                    ClientModel.is_active == True,
                )
            )
            .scalar()
            or 0
        )

        # Clients with only expired subscriptions (no active ones)
        # Get all client IDs that have active subscriptions
        clients_with_active_ids = [
            row[0]
            for row in self.db.query(func.distinct(SubscriptionModel.client_id))
            .filter(SubscriptionModel.status == SubscriptionStatusEnum.ACTIVE)
            .all()
        ]
        
        if clients_with_active_ids:
            # Clients with expired subscriptions but no active ones
            with_expired_subscription = (
                self.db.query(func.count(func.distinct(ClientModel.id)))
                .join(SubscriptionModel, ClientModel.id == SubscriptionModel.client_id)
                .filter(
                    and_(
                        SubscriptionModel.status == SubscriptionStatusEnum.EXPIRED,
                        ~ClientModel.id.in_(clients_with_active_ids),
                    )
                )
                .scalar()
                or 0
            )
        else:
            # If no active subscriptions, all expired subscriptions count
            with_expired_subscription = (
                self.db.query(func.count(func.distinct(ClientModel.id)))
                .join(SubscriptionModel, ClientModel.id == SubscriptionModel.client_id)
                .filter(SubscriptionModel.status == SubscriptionStatusEnum.EXPIRED)
                .scalar()
                or 0
            )

        # Clients with pending payment
        with_pending_payment = (
            self.db.query(func.count(func.distinct(ClientModel.id)))
            .join(SubscriptionModel, ClientModel.id == SubscriptionModel.client_id)
            .filter(SubscriptionModel.status == SubscriptionStatusEnum.PENDING_PAYMENT)
            .scalar()
            or 0
        )

        return ClientStats(
            total=total,
            active=active,
            inactive=inactive,
            new_in_period=new_in_period,
            with_active_subscription=with_active_subscription,
            with_expired_subscription=with_expired_subscription,
            with_pending_payment=with_pending_payment,
        )

    def get_subscription_stats(self, period_dates: Optional[Dict[str, date]] = None) -> SubscriptionStats:
        """Get subscription statistics."""
        today = date.today()
        seven_days_later = today + timedelta(days=7)
        seven_days_ago = today - timedelta(days=7)

        # Count by status
        total = self.db.query(func.count(SubscriptionModel.id)).scalar() or 0
        active = (
            self.db.query(func.count(SubscriptionModel.id))
            .filter(SubscriptionModel.status == SubscriptionStatusEnum.ACTIVE)
            .scalar()
            or 0
        )
        expired = (
            self.db.query(func.count(SubscriptionModel.id))
            .filter(SubscriptionModel.status == SubscriptionStatusEnum.EXPIRED)
            .scalar()
            or 0
        )
        pending_payment = (
            self.db.query(func.count(SubscriptionModel.id))
            .filter(SubscriptionModel.status == SubscriptionStatusEnum.PENDING_PAYMENT)
            .scalar()
            or 0
        )
        canceled = (
            self.db.query(func.count(SubscriptionModel.id))
            .filter(SubscriptionModel.status == SubscriptionStatusEnum.CANCELED)
            .scalar()
            or 0
        )
        scheduled = (
            self.db.query(func.count(SubscriptionModel.id))
            .filter(SubscriptionModel.status == SubscriptionStatusEnum.SCHEDULED)
            .scalar()
            or 0
        )

        # Expiring soon (active subscriptions expiring in next 7 days)
        expiring_soon = (
            self.db.query(func.count(SubscriptionModel.id))
            .filter(
                and_(
                    SubscriptionModel.status == SubscriptionStatusEnum.ACTIVE,
                    SubscriptionModel.end_date >= today,
                    SubscriptionModel.end_date <= seven_days_later,
                )
            )
            .scalar()
            or 0
        )

        # Expired recently (expired in last 7 days)
        expired_recently = (
            self.db.query(func.count(SubscriptionModel.id))
            .filter(
                and_(
                    SubscriptionModel.status == SubscriptionStatusEnum.EXPIRED,
                    SubscriptionModel.end_date >= seven_days_ago,
                    SubscriptionModel.end_date <= today,
                )
            )
            .scalar()
            or 0
        )

        return SubscriptionStats(
            total=total,
            active=active,
            expired=expired,
            pending_payment=pending_payment,
            canceled=canceled,
            scheduled=scheduled,
            expiring_soon=expiring_soon,
            expired_recently=expired_recently,
        )

    def get_financial_stats(self, period_dates: Dict[str, date]) -> FinancialStats:
        """Get financial statistics filtered by date range."""
        period_start = datetime.combine(period_dates["start"], datetime.min.time())
        period_end = datetime.combine(period_dates["end"], datetime.max.time())
        period_start_utc, _ = get_date_range_utc(period_start)
        _, period_end_utc = get_date_range_utc(period_end)

        # Period revenue
        period_revenue = (
            self.db.query(func.coalesce(func.sum(PaymentModel.amount), 0))
            .filter(
                and_(
                    PaymentModel.payment_date >= period_start_utc,
                    PaymentModel.payment_date <= period_end_utc,
                )
            )
            .scalar()
            or Decimal("0.00")
        )

        # Payments count in period
        payments_count = (
            self.db.query(func.count(PaymentModel.id))
            .filter(
                and_(
                    PaymentModel.payment_date >= period_start_utc,
                    PaymentModel.payment_date <= period_end_utc,
                )
            )
            .scalar()
            or 0
        )

        # Average payment in period
        average_payment = (
            Decimal(str(period_revenue)) / payments_count
            if payments_count > 0
            else Decimal("0.00")
        )

        # Revenue by method
        revenue_by_method_cash = (
            self.db.query(func.coalesce(func.sum(PaymentModel.amount), 0))
            .filter(
                and_(
                    PaymentModel.payment_method == PaymentMethodEnum.CASH,
                    PaymentModel.payment_date >= period_start_utc,
                    PaymentModel.payment_date <= period_end_utc,
                )
            )
            .scalar()
            or Decimal("0.00")
        )

        revenue_by_method_qr = (
            self.db.query(func.coalesce(func.sum(PaymentModel.amount), 0))
            .filter(
                and_(
                    PaymentModel.payment_method == PaymentMethodEnum.QR,
                    PaymentModel.payment_date >= period_start_utc,
                    PaymentModel.payment_date <= period_end_utc,
                )
            )
            .scalar()
            or Decimal("0.00")
        )

        # Pending debt
        # Calculate debt as: plan price - total paid for subscriptions with pending_payment status
        pending_subscriptions = (
            self.db.query(SubscriptionModel)
            .options(joinedload(SubscriptionModel.plan))
            .filter(SubscriptionModel.status == SubscriptionStatusEnum.PENDING_PAYMENT)
            .all()
        )

        debt_count = len(pending_subscriptions)
        pending_debt = Decimal("0.00")

        for sub in pending_subscriptions:
            total_paid = (
                self.db.query(func.coalesce(func.sum(PaymentModel.amount), 0))
                .filter(PaymentModel.subscription_id == sub.id)
                .scalar()
                or Decimal("0.00")
            )
            plan_price = Decimal(str(sub.plan.price))
            remaining = max(plan_price - total_paid, Decimal("0.00"))
            pending_debt += remaining

        return FinancialStats(
            period_revenue=f"{period_revenue:.2f}",
            pending_debt=f"{pending_debt:.2f}",
            debt_count=debt_count,
            average_payment=f"{average_payment:.2f}",
            payments_count=payments_count,
            revenue_by_method=RevenueByMethod(
                cash=f"{revenue_by_method_cash:.2f}",
                qr=f"{revenue_by_method_qr:.2f}",
            ),
        )

    def get_attendance_stats(
        self, period_dates: Dict[str, date], active_clients: int
    ) -> AttendanceStats:
        """Get attendance statistics filtered by date range."""
        period_start = datetime.combine(period_dates["start"], datetime.min.time())
        period_end = datetime.combine(period_dates["end"], datetime.max.time())
        period_start_utc, _ = get_date_range_utc(period_start)
        _, period_end_utc = get_date_range_utc(period_end)

        # Total attendances in period
        total_attendances = (
            self.db.query(func.count(AttendanceModel.id))
            .filter(
                and_(
                    AttendanceModel.check_in >= period_start_utc,
                    AttendanceModel.check_in <= period_end_utc,
                )
            )
            .scalar()
            or 0
        )

        # Peak hour
        peak_hour_result = (
            self.db.query(
                extract("hour", AttendanceModel.check_in).label("hour"),
                func.count(AttendanceModel.id).label("count"),
            )
            .filter(
                and_(
                    AttendanceModel.check_in >= period_start_utc,
                    AttendanceModel.check_in <= period_end_utc,
                )
            )
            .group_by(extract("hour", AttendanceModel.check_in))
            .order_by(func.count(AttendanceModel.id).desc())
            .first()
        )

        peak_hour = (
            f"{int(peak_hour_result[0]):02d}:00" if peak_hour_result else "00:00"
        )

        # Average daily
        days_in_period = (period_dates["end"] - period_dates["start"]).days + 1
        average_daily = (
            float(total_attendances) / days_in_period if days_in_period > 0 else 0.0
        )

        # Unique visitors
        unique_visitors = (
            self.db.query(func.count(func.distinct(AttendanceModel.client_id)))
            .filter(
                and_(
                    AttendanceModel.check_in >= period_start_utc,
                    AttendanceModel.check_in <= period_end_utc,
                )
            )
            .scalar()
            or 0
        )

        # Attendance rate
        attendance_rate = (
            (unique_visitors / active_clients * 100) if active_clients > 0 else 0.0
        )

        return AttendanceStats(
            total_attendances=total_attendances,
            peak_hour=peak_hour,
            average_daily=average_daily,
            unique_visitors=unique_visitors,
            attendance_rate=attendance_rate,
        )

    def get_inventory_stats(self, period_dates: Dict[str, date]) -> InventoryStats:
        """Get inventory statistics filtered by date range."""
        period_start = datetime.combine(period_dates["start"], datetime.min.time())
        period_end = datetime.combine(period_dates["end"], datetime.max.time())
        period_start_utc, _ = get_date_range_utc(period_start)
        _, period_end_utc = get_date_range_utc(period_end)

        # Basic stats
        total_products = self.db.query(func.count(ProductModel.id)).scalar() or 0
        active_products = (
            self.db.query(func.count(ProductModel.id))
            .filter(ProductModel.is_active == True)
            .scalar()
            or 0
        )

        # Low stock, out of stock, overstock
        low_stock_count = (
            self.db.query(func.count(ProductModel.id))
            .filter(
                and_(
                    ProductModel.is_active == True,
                    ProductModel.available_quantity > 0,
                    ProductModel.available_quantity < ProductModel.min_stock,
                )
            )
            .scalar()
            or 0
        )

        out_of_stock_count = (
            self.db.query(func.count(ProductModel.id))
            .filter(
                and_(
                    ProductModel.is_active == True,
                    ProductModel.available_quantity == 0,
                )
            )
            .scalar()
            or 0
        )

        overstock_count = (
            self.db.query(func.count(ProductModel.id))
            .filter(
                and_(
                    ProductModel.is_active == True,
                    ProductModel.max_stock.isnot(None),
                    ProductModel.available_quantity > ProductModel.max_stock,
                )
            )
            .scalar()
            or 0
        )

        # Total inventory value and units
        products = (
            self.db.query(ProductModel)
            .filter(ProductModel.is_active == True)
            .all()
        )
        total_inventory_value = sum(
            p.available_quantity * p.price for p in products
        )
        total_units = sum(p.available_quantity for p in products)

        # Sales in period (EXIT movements)
        sales_period_query = (
            self.db.query(
                func.count(InventoryMovementModel.id),
                func.coalesce(func.sum(func.abs(InventoryMovementModel.quantity)), 0),
                func.coalesce(
                    func.sum(
                        func.abs(InventoryMovementModel.quantity) * ProductModel.price
                    ),
                    0,
                ),
            )
            .join(ProductModel, InventoryMovementModel.product_id == ProductModel.id)
            .filter(
                and_(
                    InventoryMovementModel.movement_type == InventoryMovementTypeEnum.EXIT,
                    InventoryMovementModel.movement_date >= period_start_utc,
                    InventoryMovementModel.movement_date <= period_end_utc,
                )
            )
        ).first()

        sales_period_units = int(sales_period_query[1] or 0)
        sales_period_amount = sales_period_query[2] or Decimal("0.00")
        sales_period_transactions = sales_period_query[0] or 0

        return InventoryStats(
            total_products=total_products,
            active_products=active_products,
            low_stock_count=low_stock_count,
            out_of_stock_count=out_of_stock_count,
            overstock_count=overstock_count,
            total_inventory_value=f"{total_inventory_value:.2f}",
            total_units=Decimal(str(total_units)),
            sales_in_period=SalesInfo(
                units=sales_period_units,
                amount=f"{sales_period_amount:.2f}",
                transactions=sales_period_transactions,
            ),
        )

    def get_recent_activities(self, limit: int = 20) -> List[RecentActivity]:
        """Get recent activities from multiple sources."""
        activities: List[RecentActivity] = []
        # Calculate 24 hours ago in local time, then convert to UTC
        # Get current time in local timezone
        now_local = TIMEZONE.localize(datetime.now())
        last_24h_local = now_local - timedelta(hours=24)
        # Convert to UTC
        last_24h_utc = last_24h_local.astimezone(timezone.utc)

        # Check-ins
        check_ins = (
            self.db.query(AttendanceModel, ClientModel)
            .join(ClientModel, AttendanceModel.client_id == ClientModel.id)
            .filter(AttendanceModel.check_in >= last_24h_utc)
            .order_by(AttendanceModel.check_in.desc())
            .limit(limit)
            .all()
        )

        for attendance, client in check_ins:
            activities.append(
                RecentActivity(
                    id=f"check_in_{attendance.id}",
                    type="check_in",
                    description=f"{client.first_name} {client.last_name} ingresó al gimnasio",
                    timestamp=attendance.check_in,
                    client_id=str(client.id),
                    client_name=f"{client.first_name} {client.last_name}",
                    metadata=ActivityMetadata(attendance_id=str(attendance.id)),
                )
            )

        # Payments
        payments = (
            self.db.query(PaymentModel, SubscriptionModel, ClientModel)
            .join(SubscriptionModel, PaymentModel.subscription_id == SubscriptionModel.id)
            .join(ClientModel, SubscriptionModel.client_id == ClientModel.id)
            .filter(PaymentModel.payment_date >= last_24h_utc)
            .order_by(PaymentModel.payment_date.desc())
            .limit(limit)
            .all()
        )

        for payment, subscription, client in payments:
            activities.append(
                RecentActivity(
                    id=f"payment_{payment.id}",
                    type="payment_received",
                    description=f"{client.first_name} {client.last_name} realizó un pago de ${payment.amount:,.0f}",
                    timestamp=payment.payment_date,
                    client_id=str(client.id),
                    client_name=f"{client.first_name} {client.last_name}",
                    metadata=ActivityMetadata(
                        payment_id=str(payment.id),
                        amount=f"{payment.amount:.2f}",
                        method=payment.payment_method.value,
                    ),
                )
            )

        # New clients
        new_clients = (
            self.db.query(ClientModel)
            .filter(ClientModel.created_at >= last_24h_utc)
            .order_by(ClientModel.created_at.desc())
            .limit(limit)
            .all()
        )

        for client in new_clients:
            activities.append(
                RecentActivity(
                    id=f"client_{client.id}",
                    type="client_registration",
                    description=f"Nuevo cliente registrado: {client.first_name} {client.last_name}",
                    timestamp=client.created_at,
                    client_id=str(client.id),
                    client_name=f"{client.first_name} {client.last_name}",
                    metadata=ActivityMetadata(),
                )
            )

        # New subscriptions
        new_subscriptions = (
            self.db.query(SubscriptionModel, ClientModel)
            .join(ClientModel, SubscriptionModel.client_id == ClientModel.id)
            .options(joinedload(SubscriptionModel.plan))
            .filter(SubscriptionModel.created_at >= last_24h_utc)
            .order_by(SubscriptionModel.created_at.desc())
            .limit(limit)
            .all()
        )

        for subscription, client in new_subscriptions:
            activities.append(
                RecentActivity(
                    id=f"subscription_{subscription.id}",
                    type="subscription_created",
                    description=f"Nueva suscripción creada para {client.first_name} {client.last_name}",
                    timestamp=subscription.created_at,
                    client_id=str(client.id),
                    client_name=f"{client.first_name} {client.last_name}",
                    metadata=ActivityMetadata(
                        subscription_id=str(subscription.id),
                        plan_name=subscription.plan.name if subscription.plan else "N/A",
                    ),
                )
            )

        # Sort by timestamp DESC and limit
        activities.sort(key=lambda x: x.timestamp, reverse=True)
        return activities[:limit]

    def generate_alerts(
        self,
        subscription_stats: SubscriptionStats,
        inventory_stats: InventoryStats,
        financial_stats: FinancialStats,
    ) -> List[Alert]:
        """Generate system alerts."""
        alerts: List[Alert] = []

        # Low stock
        if inventory_stats.low_stock_count > 0:
            alerts.append(
                Alert(
                    type="low_stock",
                    severity="warning",
                    message=f"{inventory_stats.low_stock_count} productos con stock bajo",
                    count=inventory_stats.low_stock_count,
                    total_amount=None,
                )
            )

        # Out of stock
        if inventory_stats.out_of_stock_count > 0:
            alerts.append(
                Alert(
                    type="out_of_stock",
                    severity="error",
                    message=f"{inventory_stats.out_of_stock_count} productos sin stock",
                    count=inventory_stats.out_of_stock_count,
                    total_amount=None,
                )
            )

        # Subscriptions expiring
        if subscription_stats.expiring_soon > 0:
            alerts.append(
                Alert(
                    type="subscriptions_expiring",
                    severity="info",
                    message=f"{subscription_stats.expiring_soon} suscripciones expiran en los próximos 7 días",
                    count=subscription_stats.expiring_soon,
                    total_amount=None,
                )
            )

        # Pending debt
        if financial_stats.debt_count > 0:
            alerts.append(
                Alert(
                    type="pending_debt",
                    severity="warning",
                    message=f"{financial_stats.debt_count} suscripciones con pagos pendientes",
                    count=financial_stats.debt_count,
                    total_amount=financial_stats.pending_debt,
                )
            )

        return alerts

    def get_statistics(self, start_date: date, end_date: date) -> StatisticsResponse:
        """
        Get comprehensive statistics for admin dashboard filtered by date range.

        Args:
            start_date: Start date of the range
            end_date: End date of the range

        Returns:
            StatisticsResponse with all aggregated data filtered by date range
        """
        period_dates = {"start": start_date, "end": end_date}

        # Get all statistics (all filtered by the date range)
        client_stats = self.get_client_stats(period_dates)
        subscription_stats = self.get_subscription_stats(period_dates)
        financial_stats = self.get_financial_stats(period_dates)
        attendance_stats = self.get_attendance_stats(
            period_dates, client_stats.active
        )
        inventory_stats = self.get_inventory_stats(period_dates)
        alerts = self.generate_alerts(
            subscription_stats, inventory_stats, financial_stats
        )

        return StatisticsResponse(
            period=PeriodInfo(
                start_date=start_date,
                end_date=end_date,
            ),
            client_stats=client_stats,
            subscription_stats=subscription_stats,
            financial_stats=financial_stats,
            attendance_stats=attendance_stats,
            inventory_stats=inventory_stats,
            alerts=alerts,
            generated_at=datetime.now(timezone.utc),
        )

