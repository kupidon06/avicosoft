from django.apps import AppConfig

class VentesConfig(AppConfig):
    name = 'apps.ventes'

    def ready(self):
        # Importer les signaux
        import apps.ventes.signals
