from django.db import models
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from kake.models.mixins import TenantMixin, DomainMixin
from apps.users.models import User
import uuid

# Choix constants
PLAN_CHOICES = [
    ('free', 'Gratuit'),
    ('pro', 'Pro'),
    ('enterprise', 'Entreprise'),
]

ORDER_STATUS_CHOICES = [
    ('pending', 'Pending'),
    ('completed', 'Completed'),
    ('cancelled', 'Cancelled'),
]

PAYMENT_METHOD_CHOICES = [
    ('cash', 'Cash'),
    ('credit_card', 'Credit Card'),
    ('paypal', 'PayPal'),
]

PAYMENT_STATUS_CHOICES = [
    ('pending', 'Pending'),
    ('paid', 'Paid'),
    ('failed', 'Failed'),
]


class Subscription(models.Model):
    company = models.ForeignKey('Company', on_delete=models.CASCADE, related_name='subscriptions')
    plan = models.CharField(max_length=20, choices=PLAN_CHOICES, default='free')
    subscription_date = models.DateTimeField(auto_now_add=True)
    start_date = models.DateTimeField(null=True, blank=True)
    end_date = models.DateTimeField(null=True, blank=True)
    active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.company.name} - {self.get_plan_display()}"


class Company(TenantMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='companies')
    name = models.CharField(max_length=255, unique=True)
    email = models.EmailField(max_length=500, unique=True)
    phone = models.CharField(max_length=15, null=True, blank=True, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    subscription_plan = models.CharField(max_length=50, choices=PLAN_CHOICES, default='free')
    is_active = models.BooleanField(default=True)

    def clean(self):
        if Company.objects.filter(schema_name=self.schema_name).exists():
            raise ValidationError(_("Le schéma '%(schema_name)s' existe déjà.") % {'schema_name': self.schema_name})
        super().clean()

    def __str__(self):
        return self.name
    def save(self, *args, **kwargs):
        self.schema_name = self.name
        super().save(*args, **kwargs)
    


class Domain(DomainMixin):
    pass


class Payment(models.Model):
    subscription = models.ForeignKey(Subscription, on_delete=models.CASCADE, related_name='payments')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending')
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES, default='cash')
    transaction_id = models.CharField(max_length=100, null=True, blank=True)
    payment_date = models.DateField(auto_now_add=True)
    remark = models.TextField(blank=True)

    def __str__(self):
        return f"Payment of {self.amount} for subscription {self.subscription.id}"

    def clean(self):
        # Validation logic can be added here if needed
        pass