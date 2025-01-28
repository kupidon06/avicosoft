from allauth.account.adapter import get_adapter
from allauth.account.utils import setup_user_email
from .models import User, EmployeeProfile, Fournisseur, Absence
from drf_spectacular.utils import extend_schema
from rest_framework import serializers
from django.core.exceptions import ValidationError
import datetime
from pytz import timezone


class CustomRegisterSerializer(serializers.ModelSerializer):
    password1 = serializers.CharField(write_only=True)
    password2 = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['email', 'name', 'phone', 'password1', 'password2', 'role']

    def validate_password1(self, password):
        return get_adapter().clean_password(password)

    def validate_email(self, email):
        if User.objects.filter(email=email).exists():
            raise serializers.ValidationError("Un utilisateur avec cet email existe déjà.")
        return email

    def validate_phone(self, phone):
        if User.objects.filter(phone=phone).exists():
            raise serializers.ValidationError("Un utilisateur avec ce numéro de téléphone existe déjà.")
        return phone

    def validate(self, data):
        if data['password1'] != data['password2']:
            raise serializers.ValidationError("Les deux champs de mot de passe ne correspondent pas.")
        return data

    def save(self, request):
        adapter = get_adapter()
        user = adapter.new_user(request)
        self.cleaned_data = self.get_cleaned_data()
        adapter.save_user(request, user, self)
        setup_user_email(request, user, [])
        user.save()
        return user

    def get_cleaned_data(self):
        return {
            'password1': self.validated_data.get('password1', ''),
            'email': self.validated_data.get('email', ''),
            'name': self.validated_data.get('name', ''),
            'phone': self.validated_data.get('phone', ''),
            'role': self.validated_data.get('role', 'customer'),
        }

class ForgotPasswordInputSerializer(serializers.Serializer):
    email = serializers.EmailField()

class PasswordResetSerializer(serializers.Serializer):
    new_password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)

    def validate(self, data):
        if data['new_password'] != data['confirm_password']:
            raise serializers.ValidationError("Les mots de passe ne correspondent pas.")
        return data

    def save(self, user):
        user.set_password(self.validated_data['new_password'])
        user.save()
        return user

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'name', 'username', 'phone', 'email', 'role', 'is_active', 'is_staff', 'date_joined', 'last_login']

    def validate_email(self, email):
        if User.objects.filter(email=email).exists():
            raise serializers.ValidationError("A user with that email already exists.")
        return email

    def validate_phone(self, phone):
        if User.objects.filter(phone=phone).exists():
            raise serializers.ValidationError("A user with that phone number already exists.")
        return phone

class EmployeeProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = EmployeeProfile
        fields = ['user', 'position', 'salary', 'identity']

    def validate_salary(self, salary):
        if salary < 0:
            raise serializers.ValidationError("Salary cannot be negative.")
        return salary

class FournisseurSerializer(serializers.ModelSerializer):
    class Meta:
        model = Fournisseur
        fields = ['id', 'name', 'phone', 'address', 'details']

    def validate_phone(self, phone):
        if Fournisseur.objects.filter(phone=phone).exists():
            raise serializers.ValidationError("A fournisseur with that phone number already exists.")
        return phone

class AbsenceSerializer(serializers.ModelSerializer):
   

    class Meta:
        model = Absence
        fields = ['id', 'employee', 'date', 'reason', 'approved', 'approved_by', 'approved_at']

    def validate_date(self, date):
        if date < datetime.date.today():
            raise serializers.ValidationError("Absence date cannot be in the past.")
        return date
