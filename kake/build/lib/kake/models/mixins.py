from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings



class TenantMixin(models.Model):
    schema_name = models.CharField(
        max_length=63, 
        unique=True, 
        help_text=_("Nom du schéma associé à ce tenant. Doit être unique.")
    )
    name = models.CharField(
        max_length=255, 
        help_text=_("Nom lisible associé à ce tenant.")
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

    def __str__(self):
        return self.name


class DomainMixin(models.Model):
    domain = models.CharField(
        max_length=255, 
        unique=True, 
        help_text=_("Nom de domaine associé à ce tenant.")
    )
    tenant = models.ForeignKey(
        settings.TENANT_MODEL, 
        on_delete=models.CASCADE, 
        related_name='domains',
        help_text=_("Le tenant associé à ce domaine.")
    )
    is_primary = models.BooleanField(
        default=False, 
        help_text=_("Ce domaine est-il le domaine principal du tenant ?")
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

    def __str__(self):
        return self.domain
