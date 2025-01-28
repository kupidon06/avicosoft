from django.http import HttpResponseForbidden

class TenantRequiredMixin:
    def dispatch(self, request, *args, **kwargs):
        # Check if the tenant attribute exists on the request
        if not hasattr(request, 'tenant') or not request.tenant:
            return HttpResponseForbidden("Aucun tenant n'est associé à cette requête.")
        return super().dispatch(request, *args, **kwargs)
