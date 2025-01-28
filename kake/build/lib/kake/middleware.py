from django.utils.deprecation import MiddlewareMixin
from django.db import connection
from django.http import HttpResponseForbidden
from django.conf import settings
from django.apps import apps
import re

class TenantMiddleware(MiddlewareMixin):
    def process_request(self, request):
        # Récupérer le domaine de la requête
        host = request.get_host()
        Tenant = apps.get_model(settings.TENANT_MODEL)

        # Enlever le port du domaine si présent
        domain_without_port = host.split(":")[0]

        # Récupérer la liste des domaines publics depuis les settings
        public_domains = getattr(settings, "TENANT_PUBLIC_DOMAINS", [])

        # Vérifier si le domaine fait partie des domaines publics
        if domain_without_port in public_domains:
            schema_name = "public"
        else:
            # Extraire la première partie du sous-domaine
            domain_parts = domain_without_port.split('.')

            # Si aucun sous-domaine n'est présent, utiliser le schéma public
            if len(domain_parts) < 2:  # ex : localhost.com ou example.com
                schema_name = "public"
            else:
                # Utiliser la première partie comme schéma, après validation
                schema_name = domain_parts[0]

                # Validation stricte du schéma (alphanumérique et underscores seulement)
                if not re.match(r'^[a-zA-Z0-9_]+$', schema_name):
                    return HttpResponseForbidden("Nom du schéma invalide.")

        try:
            # Vérifier que le tenant existe si le schéma n'est pas 'public'
            if schema_name != "public":
                tenant = Tenant.objects.get(schema_name=schema_name)
                # Ajouter le tenant au request pour un usage ultérieur
                request.tenant = tenant
            else:
                tenant = None  # Aucun tenant spécifique pour le schéma public
                request.tenant = None

            # Mettre à jour le search_path PostgreSQL pour utiliser le schéma
            with connection.cursor() as cursor:
                cursor.execute("SET search_path TO %s;", [schema_name])

        except Tenant.DoesNotExist:
            return HttpResponseForbidden("Tenant non trouvé.")

        except Exception as e:
            print(f"Erreur lors de la configuration du tenant : {str(e)}")  # Pour déboguer
            return HttpResponseForbidden(f"Erreur lors de la configuration du tenant : {str(e)}")
