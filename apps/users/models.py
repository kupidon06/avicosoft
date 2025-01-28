from django.db import models
from django.utils.crypto import get_random_string
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin, Group, Permission
import uuid

class ModificationHistory(models.Model):
    user = models.ForeignKey('User', on_delete=models.CASCADE)
    field_name = models.CharField(max_length=255)
    old_value = models.TextField(null=True, blank=True)
    new_value = models.TextField(null=True, blank=True)
    changed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.field_name} changé par {self.user.name} à {self.changed_at}"

class UserAccountManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("L'email doit être fourni.")
        if not extra_fields.get('phone'):
            raise ValueError("Le numéro de téléphone doit être fourni.")
        phone = extra_fields.get('phone')
        if self.model.objects.filter(phone=phone).exists():
            raise ValueError(f"Un utilisateur avec le numéro de téléphone {phone} existe déjà.")

        email = self.normalize_email(email)
        extra_fields.setdefault('username', email.split('@')[0])  # Génère un username par défaut
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.activation_code = get_random_string(length=32)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if not extra_fields.get('username'):
            raise ValueError("Le nom doit être fourni pour le superutilisateur.")
        if not extra_fields.get('email'):
            raise ValueError("L'email  doit être fourni pour le superutilisateur.")

        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    ROLE_CHOICES = [
        ('admin', 'Administrateur'),
        ('customer', 'Client'),
        ('cashier', 'Caissier'),
        ('veterinarian', 'Vétérinaire'),
        ('accountant', 'Comptable'),
        ('employee', 'Employé'),
        ('manager', 'Responsable'),
        ('farmer', 'Fermier'),
        
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=500, null=True)
    username = models.CharField(max_length=150, unique=True, null=False, blank=False)
    phone = models.CharField(max_length=15, null=True, blank=True, unique=True)
    email = models.EmailField(max_length=500, null=True, blank=True, unique=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='customer')
    is_active = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(auto_now=True)

    objects = UserAccountManager()

    groups = models.ManyToManyField(
        Group,
        related_name='custom_user_set',
        blank=True,
        help_text='Les groupes auxquels cet utilisateur appartient.',
        verbose_name='Groupes',
    )
    user_permissions = models.ManyToManyField(
        Permission,
        related_name='custom_user_permissions_set',
        blank=True,
        help_text='Permissions spécifiques pour cet utilisateur.',
        verbose_name='Permissions utilisateur',
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name', 'phone']

    def __str__(self):
        return self.email or self.name

class EmployeeProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    position = models.CharField(max_length=200)
    salary = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    identity = models.ImageField(upload_to='identity/', blank=True, null=True)

    def __str__(self):
        return f"{self.user.name} - {self.position}"

class Fournisseur(models.Model):
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=15, null=True, blank=True, unique=True)
    phone = models.CharField(max_length=100, blank=True)
    address = models.TextField(blank=True)
    details=models.TextField(blank=True)

    def __str__(self):
        return self.name

class Absence(models.Model):
    employee = models.ForeignKey(EmployeeProfile, on_delete=models.CASCADE)
    date = models.DateField()
    reason = models.TextField()
    approved = models.BooleanField(default=False)
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_absences')
    approved_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.employee.user.name} - {self.date}"
