from django.apps import AppConfig

class ProduitsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.produits'

    def ready(self):
        import apps.produits.signals
