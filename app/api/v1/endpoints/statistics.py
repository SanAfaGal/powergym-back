"""
Statistics Endpoint

FastAPI endpoint for admin dashboard statistics.
"""

import logging
from typing import Annotated
from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_admin_user
from app.db.session import get_db
from app.schemas.user import User
from app.schemas.statistics import StatisticsResponse, RecentActivity
from app.services.statistics_service import StatisticsService

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get(
    "/statistics",
    response_model=StatisticsResponse,
    summary="Get comprehensive admin dashboard statistics",
    description="""
    Get consolidated statistics and metrics for the admin dashboard filtered by date range.
    
    This endpoint aggregates data from multiple sources (clients, subscriptions,
    payments, attendances, inventory) to provide a comprehensive view of the
    gym's operations for a specific date range.
    
    **Required permissions:** Admin only
    
    **Query Parameters:**
    - start_date: Start date of the range in YYYY-MM-DD format (required)
    - end_date: End date of the range in YYYY-MM-DD format (required)
    
    **Response includes:**
    - Date range information
    - Client statistics (filtered by range)
    - Subscription statistics
    - Financial statistics (filtered by range)
    - Attendance statistics (filtered by range)
    - Inventory statistics (sales filtered by range)
    - System alerts
    
    **Note:** Recent activities are not included in this endpoint.
    Use /api/v1/statistics/recent-activities for recent activities (last 24 hours).
    """,
    responses={
        200: {
            "description": "Statistics retrieved successfully",
            "content": {
                "application/json": {
                    "example": {
                        "period": {
                            "start_date": "2025-01-01",
                            "end_date": "2025-01-31"
                        },
                        "client_stats": {
                            "total": 850,
                            "active": 723,
                            "inactive": 127,
                            "new_in_period": 45,
                            "with_active_subscription": 698,
                            "with_expired_subscription": 125,
                            "with_pending_payment": 15
                        },
                        "subscription_stats": {
                            "total": 1850,
                            "active": 698,
                            "expired": 892,
                            "pending_payment": 15,
                            "canceled": 240,
                            "scheduled": 5,
                            "expiring_soon": 8,
                            "expired_recently": 23
                        },
                        "financial_stats": {
                            "period_revenue": "12500000.00",
                            "pending_debt": "2500000.00",
                            "debt_count": 15,
                            "average_payment": "85000.00",
                            "payments_count": 147,
                            "revenue_by_method": {
                                "cash": "8500000.00",
                                "qr": "3000000.00"
                            }
                        },
                        "attendance_stats": {
                            "total_attendances": 3845,
                            "peak_hour": "18:00",
                            "average_daily": 125.0,
                            "unique_visitors": 523,
                            "attendance_rate": 72.3
                        },
                        "inventory_stats": {
                            "total_products": 45,
                            "active_products": 42,
                            "low_stock_count": 5,
                            "out_of_stock_count": 2,
                            "overstock_count": 1,
                            "total_inventory_value": "15000000.00",
                            "total_units": 1250,
                            "sales_in_period": {
                                "units": 892,
                                "amount": "2230000.00",
                                "transactions": 312
                            }
                        },
                        "alerts": [],
                        "generated_at": "2025-01-15T18:45:30Z"
                    }
                }
            }
        },
        401: {"description": "Unauthorized - Invalid or missing token"},
        403: {"description": "Forbidden - Admin role required"},
        422: {"description": "Validation error - Invalid parameters"},
    },
)
def get_statistics(
    start_date: str = Query(
        ...,
        regex="^\\d{4}-\\d{2}-\\d{2}$",
        description="Start date of the range in YYYY-MM-DD format (required)",
    ),
    end_date: str = Query(
        ...,
        regex="^\\d{4}-\\d{2}-\\d{2}$",
        description="End date of the range in YYYY-MM-DD format (required)",
    ),
    db: Session = Depends(get_db),
    current_user: Annotated[User, Depends(get_current_admin_user)] = None,
) -> StatisticsResponse:
    """
    Get comprehensive statistics for admin dashboard filtered by date range.

    Aggregates data from clients, subscriptions, payments, attendances,
    and inventory to provide a complete operational overview for the specified
    date range.

    **Examples:**
    - `/api/v1/statistics?start_date=2025-01-01&end_date=2025-01-31` - Statistics for January 2025
    - `/api/v1/statistics?start_date=2025-01-15&end_date=2025-01-15` - Statistics for a single day
    - `/api/v1/statistics?start_date=2025-01-01&end_date=2025-01-07` - Statistics for first week of January
    """
    try:
        # Parse date parameters
        try:
            start = date.fromisoformat(start_date)
            end = date.fromisoformat(end_date)
        except ValueError:
            logger.warning(f"Invalid date format: start_date={start_date}, end_date={end_date}")
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Invalid date format. Use YYYY-MM-DD",
            )

        # Validate date range
        if start > end:
            logger.warning(f"Invalid date range: start_date={start_date} > end_date={end_date}")
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="start_date must be before or equal to end_date",
            )

        logger.info(
            f"Admin {current_user.username} requesting statistics: "
            f"start_date={start}, end_date={end}"
        )

        service = StatisticsService(db)
        statistics = service.get_statistics(start_date=start, end_date=end)

        logger.debug(f"Statistics generated successfully for range {start} to {end}")
        return statistics

    except HTTPException:
        raise
    except ValueError as e:
        logger.warning(f"Invalid date: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e),
        )
    except Exception as e:
        logger.error(f"Error generating statistics: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error generating statistics",
        )


@router.get(
    "/statistics/recent-activities",
    response_model=list[RecentActivity],
    summary="Get recent activities (last 24 hours)",
    description="""
    Get recent activities from the last 24 hours.
    
    This endpoint returns activities from multiple sources:
    - Check-ins
    - Payments received
    - New client registrations
    - New subscription creations
    
    **Required permissions:** Admin only
    
    **Note:** This endpoint does not require date filters as it always returns
    the last 24 hours of activities.
    """,
)
def get_recent_activities(
    limit: int = Query(
        default=20,
        ge=1,
        le=50,
        description="Maximum number of activities to return (default: 20, max: 50)",
    ),
    db: Session = Depends(get_db),
    current_user: Annotated[User, Depends(get_current_admin_user)] = None,
) -> list[RecentActivity]:
    """
    Get recent activities from the last 24 hours.
    
    Returns activities sorted by timestamp (most recent first).
    """
    logger.info(f"Admin {current_user.username} requesting recent activities (limit={limit})")
    
    service = StatisticsService(db)
    activities = service.get_recent_activities(limit=limit)
    
    logger.debug(f"Returning {len(activities)} recent activities")
    return activities

