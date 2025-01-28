from django import forms
from .models import Subscription,Company,Payment

class SubscriptionForm(forms.ModelForm):
    class Meta:
        model = Subscription
        fields = ['company', 'plan', 'start_date', 'end_date', 'active']


class CompanyForm(forms.ModelForm):
    class Meta:
        model = Company
        fields = ['user', 'name', 'email', 'phone', 'subscription_plan', 'is_active']
    def create(self, validated_data):
        # Assurez-vous que le champ `name` est fourni
        name = validated_data.get('name')
        if not name:
            raise serializers.ValidationError({"name": "Ce champ est obligatoire."})

        # Définir automatiquement schema_name
        validated_data['schema_name'] = name  # schema_name = name

        # Créer l'instance de la compagnie
        company = Company.objects.create(**validated_data)

        # Créer le domaine principal
        Domain.objects.create(
            tenant=company,
            domain=name,  # Utiliser `name` comme domaine principal
            is_primary=True,
        )

        return company



class PaymentForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = ['subscription', 'amount', 'payment_status', 'payment_method', 'transaction_id', 'remark']
