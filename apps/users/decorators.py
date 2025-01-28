from django.http import HttpResponseNotFound
from django.shortcuts import redirect

def role_required(excluded_roles=None):
    """
    Décorateur pour restreindre l'accès à une vue selon les rôles d'utilisateur.
    Si l'utilisateur a un rôle exclu, une erreur 404 est renvoyée.
    """
    if excluded_roles is None:
        excluded_roles = []

    def decorator(view_func):
        def _wrapped_view(request, *args, **kwargs):
            # Vérifier si l'utilisateur a un rôle exclu
            if request.user.role in excluded_roles:
                return redirect('error_404')
            return view_func(request, *args, **kwargs)

        return _wrapped_view
    return decorator