from django.http import HttpResponseForbidden
from functools import wraps

def tenant_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        # Vérifier si un tenant est associé à la requête
        if not hasattr(request, 'tenant') or not request.tenant:
            return HttpResponseForbidden("Aucun tenant n'est associé à cette requête.")
        
        # Vérifier si le schéma est bien valide dans le contexte de la requête
        if not is_valid_tenant(request.tenant):
            return HttpResponseForbidden("Tenant invalide ou inconnu.")
        
        return view_func(request, *args, **kwargs)
    
    return _wrapped_view

def is_valid_tenant(tenant_schema):
    """
    Vérifie si le schéma du tenant existe dans la base de données.
    Cette fonction peut être ajustée selon votre logique de validation des tenants.
    """
    # Ici, vous pouvez implémenter la logique de validation, par exemple en vérifiant
    # si le schéma existe dans votre base de données PostgreSQL ou si le tenant est valide
    try:
        with connection.cursor() as cursor:
            cursor.execute(f"SELECT schema_name FROM information_schema.schemata WHERE schema_name = %s;", [tenant_schema])
            return cursor.fetchone() is not None
    except Exception as e:
        return False
