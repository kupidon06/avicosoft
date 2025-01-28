from allauth.account.adapter import DefaultAccountAdapter
from django.forms import ValidationError

class CustomAccountAdapter(DefaultAccountAdapter):
    def save_user(self, request, user, form, commit=True):
        """
        Override the default save_user method to include custom fields.
        """
        user = super().save_user(request, user, form, commit=False)
        data = form.cleaned_data
        user.name = data.get('name')
        user.phone = data.get('phone')
        user.role = data.get('role', 'customer')  # Valeur par défaut si aucun rôle n'est fourni
        if commit:
            user.save()
        return user
