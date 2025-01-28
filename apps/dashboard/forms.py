from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, PasswordChangeForm, UsernameField, PasswordResetForm, SetPasswordForm
from django.utils.translation import gettext_lazy as _
from apps.users.models import User

# Formulaire d'enregistrement utilisateur
class RegistrationForm(UserCreationForm):
    COUNTRY_CHOICES = [
        ('+224', 'Guinée'),
        ('+221', 'Sénégal'),
        ('+223', 'Mali'),
        ('+225', 'Côte d\'Ivoire'),
    ]

    password1 = forms.CharField(
        label=_("Password"),
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'}),
    )
    password2 = forms.CharField(
        label=_("Confirm Password"),
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirm Password'}),
    )
    phone_country_code = forms.ChoiceField(
        label=_("Country Code"),
        choices=COUNTRY_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'}),
    )
    phone_number = forms.CharField(
        label=_("Phone Number"),
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '000000000'}),
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'phone_country_code', 'phone_number')

        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Username'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'example@company.com'
            }),
        }

    def clean(self):
        cleaned_data = super().clean()
        phone_country_code = cleaned_data.get('phone_country_code')
        phone_number = cleaned_data.get('phone_number')

        if phone_country_code and phone_number:
            full_phone_number = phone_country_code + phone_number
            if User.objects.filter(phone=full_phone_number).exists():
                raise forms.ValidationError(f"Un utilisateur avec le numéro de téléphone {full_phone_number} existe déjà.")

        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.phone = self.cleaned_data['phone_country_code'] + self.cleaned_data['phone_number']
        if commit:
            user.save()
        return user

# Formulaire de connexion utilisateur
class LoginForm(AuthenticationForm):
  username = UsernameField(label=_("Your Username"), widget=forms.TextInput(attrs={"class": "form-control mt-1 block w-full px-4 py-3 rounded-lg border border-gray-300 shadow-sm focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500 transition-colors", "placeholder": "Username"}))
  password = forms.CharField(
      label=_("Your Password"),
      strip=False,
      widget=forms.PasswordInput(attrs={"class": "form-control mt-1 block w-full px-4 py-3 rounded-lg border border-gray-300 shadow-sm focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500 transition-colors", "placeholder": "Password"}),
  )

# Formulaire de réinitialisation de mot de passe
class UserPasswordResetForm(PasswordResetForm):
    email = forms.EmailField(widget=forms.EmailInput(attrs={
        'class': 'form-control',
        'placeholder': 'Enter your email'
    }))

# Formulaire de réinitialisation du mot de passe avec le nouveau mot de passe
class UserSetPasswordForm(SetPasswordForm):
    new_password1 = forms.CharField(max_length=50, widget=forms.PasswordInput(attrs={
        'class': 'form-control', 'placeholder': 'New Password'
    }), label="New Password")
    new_password2 = forms.CharField(max_length=50, widget=forms.PasswordInput(attrs={
        'class': 'form-control', 'placeholder': 'Confirm New Password'
    }), label="Confirm New Password")

# Formulaire de changement de mot de passe
class UserPasswordChangeForm(PasswordChangeForm):
    old_password = forms.CharField(max_length=50, widget=forms.PasswordInput(attrs={
        'class': 'form-control', 'placeholder': 'Old Password'
    }), label='Old Password')
    new_password1 = forms.CharField(max_length=50, widget=forms.PasswordInput(attrs={
        'class': 'form-control', 'placeholder': 'New Password'
    }), label="New Password")
    new_password2 = forms.CharField(max_length=50, widget=forms.PasswordInput(attrs={
        'class': 'form-control', 'placeholder': 'Confirm New Password'
    }), label="Confirm New Password")
