from django.db import connection
from django.core.management import call_command
from django.core.exceptions import ValidationError
from django.conf import settings
from django.contrib.sites.models import Site
from django.contrib.auth import get_user_model

class TenantCreationMixin:
    def create_and_migrate_tenant(self, name, schema_name, domain,user):
        try:
            # Création du schéma
            with connection.cursor() as cursor:
                cursor.execute(f"CREATE SCHEMA IF NOT EXISTS {schema_name};")

            # Migration des schémas
            with connection.cursor() as cursor:
                # Utilisation de schema_name au lieu de tenant.schema_name
                cursor.execute(f"SET search_path TO {schema_name};")
                call_command('migrate', interactive=False)
                User = get_user_model()
                

                if not user.email:
                    raise ValueError("L'utilisateur connecté doit avoir un email pour créer un superutilisateur.")

                User.objects.create(
                    username=user.username or f"default_{user.id}",  # Générer un username par défaut si manquant
                    email=user.email,
                    password=user.password or "default_password",   # Fournir un mot de passe par défaut en cas d'absence
                    role='admin',
                    is_active=True
                )
            

            # Synchronisation avec le modèle Site
            full_domain = f"{domain}"
            default_site = Site.objects.get(id=1)  # Récupérer le site par défaut avec l'ID 1
            default_site.domain = full_domain     # Mettre à jour le domaine avec le tenant
            default_site.name = name              # Mettre à jour le nom avec celui du tenant
            default_site.save()

            # Synchronisation ou création d'un nouveau site si nécessaire
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
