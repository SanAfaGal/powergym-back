from datetime import datetime


class AccessValidationUtil:
    """Utilidades para validación de acceso."""

    @staticmethod
    def format_client_info(client) -> dict:
        """Formatear información del cliente."""
        return {
            "first_name": client.first_name,
            "last_name": client.last_name,
            "dni_number": client.dni_number
        }

    @staticmethod
    def format_subscription_info(subscription) -> dict:
        """Formatear información de suscripción."""
        return {
            "status": subscription.status,
            "end_date": subscription.end_date.isoformat(),
            "days_remaining": (subscription.end_date - datetime.now().date()).days
        }