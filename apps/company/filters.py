# apps/yourapp/filters.py
import django_filters
from .models import Subscription, Company, CompanyPermission, Domain

class SubscriptionFilter(django_filters.FilterSet):
    company_name = django_filters.CharFilter(field_name='company__name', lookup_expr='icontains')
    plan = django_filters.ChoiceFilter(choices=Subscription.PLAN_CHOICES)
    active = django_filters.BooleanFilter()
    start_date = django_filters.DateTimeFilter(field_name='start_date', lookup_expr='gte')
    end_date = django_filters.DateTimeFilter(field_name='end_date', lookup_expr='lte')

    class Meta:
        model = Subscription
        fields = ['company_name', 'plan', 'active', 'start_date', 'end_date']


class CompanyFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr='icontains')
    email = django_filters.CharFilter(lookup_expr='icontains')
    phone = django_filters.CharFilter(lookup_expr='icontains')
    is_active = django_filters.BooleanFilter()

    class Meta:
        model = Company
        fields = ['name', 'email', 'phone', 'is_active']


class CompanyPermissionFilter(django_filters.FilterSet):
    company_name = django_filters.CharFilter(field_name='company__name', lookup_expr='icontains')
    user_name = django_filters.CharFilter(field_name='user__name', lookup_expr='icontains')
    permission_name = django_filters.CharFilter(field_name='permission__name', lookup_expr='icontains')

    class Meta:
        model = CompanyPermission
        fields = ['company_name', 'user_name', 'permission_name']


class DomainFilter(django_filters.FilterSet):
    domaine= django_filters.CharFilter(field_name='domain', lookup_expr='icontains')
    tenant= django_filters.CharFilter(field_name='tenant', lookup_expr='icontains')
    #
    class Meta:
        model = Domain
        fields = ['tenant','domain']
