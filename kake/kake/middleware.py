from django.utils.deprecation import MiddlewareMixin
from django.db import connection
from django.shortcuts import reverse
from django.http import HttpResponseForbidden, HttpResponseRedirect
from django.conf import settings
from django.apps import apps
import re

class TenantMiddleware(MiddlewareMixin):
    def process_request(self, request):
        # Obtenez le domaine hôte à partir de la requête
        host = request.get_host()
        Tenant = apps.get_model(settings.TENANT_MODEL)

        # Supprimez le port si présent
        domain_without_port = host.split(":")[0]

        # Vérifiez si l'URL correspond à l'URL 404 pour éviter les boucles
        try:
            error_404_url = reverse(settings.URL404).lstrip("/")
            if request.path.lstrip("/") == error_404_url:
                return  # Ne faites rien, laissez la vue gérer la requête
        except Exception:
            # Si l'URL 404 n'est pas correctement définie
            return HttpResponseForbidden("Error configuring tenant: Invalid 404 URL")

        # Liste des domaines publics à partir des paramètres
        public_domains = getattr(settings, "TENANT_PUBLIC_DOMAINS", [])

        if domain_without_port in public_domains:
            schema_name = "public"
            request.urlconf = getattr(settings, "ROOT_URLCONF")  # Charger les URL publiques
        else:
            domain_parts = domain_without_port.split('.')

            if len(domain_parts) < 2:
                schema_name = "public"
                request.urlconf = getattr(settings, "ROOT_URLCONF")
            else:
                schema_name = domain_parts[0]

                # Validez le nom du schéma (alphanumérique et underscores uniquement)
                if not re.match(r'^[a-zA-Z0-9_]+$', schema_name):
                    return HttpResponseForbidden("Invalid schema name.")
                request.urlconf = getattr(settings, "TENANT_URLCONF")  # Charger les URL du locataire

        try:
            # Récupérez le locataire pour le schéma actuel
            if schema_name != "public":
                tenant = Tenant.objects.get(schema_name=schema_name)
                request.tenant = tenant
            else:
                tenant = None
                request.tenant = None

            # Mettez à jour le chemin de recherche PostgreSQL vers le schéma du locataire
            with connection.cursor() as cursor:
                cursor.execute("SET search_path TO %s;", [schema_name])

        except Tenant.DoesNotExist:
            # Redirigez vers la page 404
            return HttpResponseRedirect(reverse(settings.URL404))

        except Exception as e:
            print(f"Error configuring tenant: {str(e)}")  # Pour le débogage
            return HttpResponseForbidden(f"Error configuring tenant: {str(e)}")
