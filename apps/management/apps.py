from django.apps import AppConfig

class ManagementConfig(AppConfig):
    name = 'apps.management'

    def ready(self):
        # Importer les signaux
        import apps.management.signals
