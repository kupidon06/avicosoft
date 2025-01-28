import django_filters
from .models import User, EmployeeProfile, Fournisseur, Absence

class UserFilter(django_filters.FilterSet):
    class Meta:
        model = User
        fields = ['name', 'email', 'phone', 'role', 'is_active', 'is_staff']

class EmployeeProfileFilter(django_filters.FilterSet):
    class Meta:
        model = EmployeeProfile
        fields = ['user__name', 'position', 'salary']

class FournisseurFilter(django_filters.FilterSet):
    class Meta:
        model = Fournisseur
        fields = ['name', 'phone', 'address']

class AbsenceFilter(django_filters.FilterSet):
    class Meta:
        model = Absence
        fields = ['employee__user__name', 'date', 'reason', 'approved', 'approved_by__name']
