from datetime import datetime
from app.utils.timezone import get_today_colombia


class AccessValidationUtil:
    """Utilities for access validation."""

    @staticmethod
    def format_client_info(client) -> dict:
        """Format client information."""
        return {
            "first_name": client.first_name,
            "last_name": client.last_name,
            "dni_number": client.dni_number
        }

    @staticmethod
    def format_subscription_info(subscription) -> dict:
        """Format subscription information."""
        today = get_today_colombia()
        return {
            "status": subscription.status,
            "end_date": subscription.end_date.isoformat(),
            "days_remaining": (subscription.end_date - today).days
        }