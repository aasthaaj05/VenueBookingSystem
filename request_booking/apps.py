from django.apps import AppConfig


class RequestBookingConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'request_booking'
    
    def ready(self):
        """
        Import signals when the app is ready.
        This ensures that signals are registered when Django starts.
        """
        import request_booking.signals  # noqa