#la fiche des commandes
from django.core.management.base import BaseCommand
from django.db import connection, OperationalError
from django.conf import settings
from django.core.management import call_command
from django.apps import apps


def get_tenant_model():
    """
    Récupère le modèle Tenant défini dans les paramètres.
    """
    return apps.get_model(settings.TENANT_MODEL)


class Command(BaseCommand):
    help = "Effectue les migrations pour chaque tenant (schéma) existant, en créant le schéma si nécessaire."

    def handle(self, *args, **options):
        Tenant = get_tenant_model()
        tenants = Tenant.objects.all()

        for tenant in tenants:
            self.stdout.write(f"Traitement du tenant : {tenant.schema_name}")

            # Vérifier si le schéma existe
            if not self.schema_exists(tenant.schema_name):
                self.stdout.write(f"Schéma {tenant.schema_name} non trouvé. Création...")
                self.create_schema(tenant.schema_name)
            else:
                self.stdout.write(f"Schéma {tenant.schema_name} déjà existant.")

            # Définir le search_path sur le schéma actuel
            try:
                with connection.cursor() as cursor:
                    cursor.execute(f"SET search_path TO {tenant.schema_name};")
                    self.stdout.write(f"Migrations pour le schéma : {tenant.schema_name}")
                    call_command('migrate', interactive=False)
            except OperationalError as e:
                self.stderr.write(f"Erreur lors de la migration pour {tenant.schema_name} : {str(e)}")

        self.stdout.write(self.style.SUCCESS("Migrations terminées pour tous les tenants."))

    def schema_exists(self, schema_name):
        """
        Vérifie si un schéma PostgreSQL existe.
        """
        query = "SELECT schema_name FROM information_schema.schemata WHERE schema_name = %s;"
        with connection.cursor() as cursor:
            cursor.execute(query, [schema_name])
            return cursor.fetchone() is not None

    def create_schema(self, schema_name):
        """
        Crée un nouveau schéma PostgreSQL.
        """
        query = f"CREATE SCHEMA IF NOT EXISTS {schema_name};"
        with connection.cursor() as cursor:
            cursor.execute(query)
        self.stdout.write(f"Schéma {schema_name} créé avec succès.")
