from django.apps import AppConfig


class DeliveryConfig(AppConfig):
    name = 'apps.delivery'
    
    def ready(self):
        import apps.delivery.signals
