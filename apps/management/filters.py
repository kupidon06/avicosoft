import django_filters
from .models import (
    Expense, ExpenseCategory, Breed, Batch, Feed, Treatment, Building, DailyLog,
    Feeding, EggCollection, TreatmentHistory, Provision
)

class BreedFilter(django_filters.FilterSet):
    class Meta:
        model = Breed
        fields = ['name', 'details']

class BatchFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(field_name='name', lookup_expr='icontains')
    breed = django_filters.CharFilter(field_name='breed__name', lookup_expr='icontains')
    building = django_filters.CharFilter(field_name='building__name', lookup_expr='icontains')
    arrival_date = django_filters.DateFilter(field_name='arrival_date')
    arrival_age = django_filters.NumberFilter(field_name='arrival_age')
    arrival_quantity = django_filters.NumberFilter(field_name='arrival_quantity')
    current_quantity = django_filters.NumberFilter(field_name='current_quantity')
    deceased_quantity = django_filters.NumberFilter(field_name='deceased_quantity')
    sick_quantity = django_filters.NumberFilter(field_name='sick_quantity')
    treatment_quantity = django_filters.NumberFilter(field_name='treatment_quantity')
    total_eggs = django_filters.NumberFilter(field_name='total_eggs')
    details = django_filters.CharFilter(field_name='details', lookup_expr='icontains')

    class Meta:
        model = Batch
        fields = [
            'name', 'breed', 'building', 'arrival_date', 'arrival_age',
            'arrival_quantity', 'current_quantity', 'deceased_quantity',
            'sick_quantity', 'treatment_quantity', 'total_eggs', 'details'
        ]

class FeedFilter(django_filters.FilterSet):
    class Meta:
        model = Feed
        fields = ['name', 'details', 'unit_price', 'unit_measure']

class TreatmentFilter(django_filters.FilterSet):
    class Meta:
        model = Treatment
        fields = ['name', 'details', 'duration_days']

class BuildingFilter(django_filters.FilterSet):
    class Meta:
        model = Building
        fields = ['name', 'details', 'capacity']

class DailyLogFilter(django_filters.FilterSet):
    class Meta:
        model = DailyLog
        fields = ['batch', 'log_date', 'living_quantity', 'deceased_quantity', 'sick_quantity', 'details']

class FeedingFilter(django_filters.FilterSet):
    class Meta:
        model = Feeding
        fields = ['batch', 'feeding_date', 'quantity', 'feed_type', 'details']

class EggCollectionFilter(django_filters.FilterSet):
    class Meta:
        model = EggCollection
        fields = ['batch', 'collection_date', 'quantity']

class TreatmentHistoryFilter(django_filters.FilterSet):
    class Meta:
        model = TreatmentHistory
        fields = ['batch', 'treatment', 'treatment_date', 'details']

class ProvisionFilter(django_filters.FilterSet):
    class Meta:
        model = Provision
        fields = ['supplier', 'feed', 'quantity', 'provision_date', 'details']

class ChargeCategoryFilter(django_filters.FilterSet):
    class Meta:
        model = ExpenseCategory
        fields = ['name']

class ChargeFilter(django_filters.FilterSet):
    class Meta:
        model = Expense
        fields = ['category', 'supplier', 'batch', 'details', 'amount', 'expense_date']
