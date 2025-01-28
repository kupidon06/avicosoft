from django.db import connection
from django.core.management import call_command
from django.core.exceptions import ValidationError
from django.conf import settings
from django.contrib.sites.models import Site

class TenantCreationMixin:
    def create_and_migrate_tenant(self, name, schema_name, domain):
        try:
            # Création du schéma
            with connection.cursor() as cursor:
                cursor.execute(f"CREATE SCHEMA IF NOT EXISTS {schema_name};")

            # Migration des schémas
            with connection.cursor() as cursor:
                # Utilisation de schema_name au lieu de tenant.schema_name
                cursor.execute(f"SET search_path TO {schema_name};")
                call_command('migrate', interactive=False)
            

            # Synchronisation avec le modèle Site
            full_domain = f"{domain}.{settings.MAIN_DOMAIN}"
            site, created = Site.objects.update_or_create(
                domain=full_domain,
                defaults={"name": name},
            )


            # Retourner une réponse de succès
            return {
                "success": f"Tenant {name} avec le domaine {domain} a été créé et migré."
            }

        except Exception as e:
            # Supprimer le schéma en cas d'échec
            with connection.cursor() as cursor:
                cursor.execute(f"DROP SCHEMA IF EXISTS {schema_name} CASCADE;")
            raise ValidationError(f"Erreur critique : {str(e)}")
