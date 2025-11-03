"""
Statistics Schemas

Pydantic schemas for admin dashboard statistics endpoint.
"""

from datetime import datetime, date
from decimal import Decimal
from typing import Optional, Literal
from pydantic import BaseModel, Field


class PeriodInfo(BaseModel):
    """Information about the analysis period."""
    start_date: date = Field(..., description="Start date of the period (ISO date: YYYY-MM-DD)")
    end_date: date = Field(..., description="End date of the period (ISO date: YYYY-MM-DD)")


class ClientStats(BaseModel):
    """Client statistics."""
    total: int = Field(..., description="Total clients in the system")
    active: int = Field(..., description="Clients with is_active = true")
    inactive: int = Field(..., description="Clients with is_active = false")
    new_in_period: int = Field(..., description="Clients created within the selected date range")
    with_active_subscription: int = Field(..., description="Clients with at least one active subscription")
    with_expired_subscription: int = Field(..., description="Clients with only expired subscriptions")
    with_pending_payment: int = Field(..., description="Clients with subscriptions in pending_payment status")


class SubscriptionStats(BaseModel):
    """Subscription statistics."""
    total: int = Field(..., description="Total subscriptions")
    active: int = Field(..., description="Subscriptions with status = 'active'")
    expired: int = Field(..., description="Subscriptions with status = 'expired'")
    pending_payment: int = Field(..., description="Subscriptions with status = 'pending_payment'")
    canceled: int = Field(..., description="Subscriptions with status = 'canceled'")
    scheduled: int = Field(..., description="Subscriptions with status = 'scheduled'")
    expiring_soon: int = Field(..., description="Active subscriptions expiring in the next 7 days")
    expired_recently: int = Field(..., description="Subscriptions that expired in the last 7 days")


class RevenueByMethod(BaseModel):
    """Revenue breakdown by payment method."""
    cash: str = Field(..., description="Revenue from cash payments (string decimal with 2 decimals)")
    qr: str = Field(..., description="Revenue from QR payments (string decimal with 2 decimals)")


class FinancialStats(BaseModel):
    """Financial statistics."""
    period_revenue: str = Field(..., description="Sum of all payments within the selected date range (string decimal)")
    pending_debt: str = Field(..., description="Total pending debt (string decimal)")
    debt_count: int = Field(..., description="Number of subscriptions with pending debt")
    average_payment: str = Field(..., description="Average payment amount within the period (string decimal)")
    payments_count: int = Field(..., description="Number of payments within the selected date range")
    revenue_by_method: RevenueByMethod = Field(..., description="Revenue breakdown by payment method within the period")


class AttendanceStats(BaseModel):
    """Attendance statistics."""
    total_attendances: int = Field(..., description="Total attendances within the selected date range")
    peak_hour: str = Field(..., description="Peak hour in HH:MM format (24 hours)")
    average_daily: float = Field(..., description="Average daily attendances in the period")
    unique_visitors: int = Field(..., description="Number of unique clients who attended in the period")
    attendance_rate: float = Field(..., description="Percentage of active clients who attended")


class SalesInfo(BaseModel):
    """Sales information for a period."""
    units: int = Field(..., description="Total units sold")
    amount: str = Field(..., description="Total amount in COP (string decimal)")
    transactions: int = Field(..., description="Number of EXIT movements")


class InventoryStats(BaseModel):
    """Inventory statistics."""
    total_products: int = Field(..., description="Total products")
    active_products: int = Field(..., description="Products with is_active = true")
    low_stock_count: int = Field(..., description="Products with available_quantity <= min_stock")
    out_of_stock_count: int = Field(..., description="Products with available_quantity = 0")
    overstock_count: int = Field(..., description="Products with available_quantity > max_stock")
    total_inventory_value: str = Field(..., description="Total inventory value (string decimal)")
    total_units: Decimal = Field(..., description="Total units in stock")
    sales_in_period: SalesInfo = Field(..., description="Sales within the selected date range")


class ActivityMetadata(BaseModel):
    """Metadata for recent activities."""
    attendance_id: Optional[str] = None
    payment_id: Optional[str] = None
    amount: Optional[str] = None
    method: Optional[str] = None
    subscription_id: Optional[str] = None
    plan_name: Optional[str] = None


class RecentActivity(BaseModel):
    """Recent activity entry."""
    id: str = Field(..., description="Unique activity ID")
    type: Literal["check_in", "payment_received", "client_registration", "subscription_created"] = Field(
        ..., description="Activity type"
    )
    description: str = Field(..., description="Human-readable description")
    timestamp: datetime = Field(..., description="Activity timestamp (ISO 8601 UTC)")
    client_id: Optional[str] = Field(None, description="Client UUID")
    client_name: Optional[str] = Field(None, description="Client full name")
    metadata: ActivityMetadata = Field(default_factory=ActivityMetadata, description="Additional metadata")


class Alert(BaseModel):
    """System alert."""
    type: Literal["low_stock", "out_of_stock", "subscriptions_expiring", "pending_debt"] = Field(
        ..., description="Alert type"
    )
    severity: Literal["error", "warning", "info"] = Field(..., description="Alert severity")
    message: str = Field(..., description="Alert message")
    count: int = Field(..., description="Number of items affected")
    total_amount: Optional[str] = Field(None, description="Total amount (only for pending_debt, string decimal)")


class StatisticsResponse(BaseModel):
    """Complete statistics response for admin dashboard."""
    period: PeriodInfo = Field(..., description="Analysis period information")
    client_stats: ClientStats = Field(..., description="Client statistics")
    subscription_stats: SubscriptionStats = Field(..., description="Subscription statistics")
    financial_stats: FinancialStats = Field(..., description="Financial statistics")
    attendance_stats: AttendanceStats = Field(..., description="Attendance statistics")
    inventory_stats: InventoryStats = Field(..., description="Inventory statistics")
    alerts: list[Alert] = Field(..., description="System alerts")
    generated_at: datetime = Field(..., description="Response generation timestamp (ISO 8601 UTC)")

    model_config = {"json_schema_extra": {"examples": []}}

