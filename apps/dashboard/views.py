from django.shortcuts import render, redirect
from .forms import RegistrationForm, LoginForm, UserPasswordResetForm, UserPasswordChangeForm, UserSetPasswordForm
from django.contrib.auth.views import LoginView, PasswordResetView, PasswordChangeView, PasswordResetConfirmView
from django.contrib.auth import logout
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.core.mail import send_mail
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.auth.tokens import default_token_generator
from .forms import RegistrationForm, LoginForm, UserPasswordResetForm, UserPasswordChangeForm, UserSetPasswordForm
from apps.management.models import Batch
from apps.users.decorators import role_required


from django.contrib.auth.decorators import login_required


def index(request):
  return render(request, 'pages/test.html')



@login_required(login_url="/accounts/login/")

def dashboard(request):
  if request.user.role=='customer':
    return render(request, 'pages/redirect.html')

  batches = Batch.objects.all()


  context = {
    'segment': 'dashboard',
    'batches':batches 
  }
  return render(request, 'dashboard/index.html', context)

# Pages
@login_required(login_url="/accounts/login/")
def transaction(request):
  context = {
    'segment': 'transactions'
  }
  return render(request, 'pages/transactions.html', context)

@login_required(login_url="/accounts/login/")
def settings(request):
  context = {
    'segment': 'settings'
  }
  return render(request, 'pages/settings.html', context)

# Tables
@login_required(login_url="/accounts/login/")
def bs_tables(request):
  context = {
    'parent': 'tables',
    'segment': 'bs_tables',
  }
  return render(request, 'pages/tables/bootstrap-tables.html', context)

# Components
@login_required(login_url="/accounts/login/")
def buttons(request):
  context = {
    'parent': 'components',
    'segment': 'buttons',
  }
  return render(request, 'pages/components/buttons.html', context)

@login_required(login_url="/accounts/login/")
def notifications(request):
  context = {
    'parent': 'components',
    'segment': 'notifications',
  }
  return render(request, 'pages/components/notifications.html', context)

@login_required(login_url="/accounts/login/")
def forms(request):
  context = {
    'parent': 'components',
    'segment': 'forms',
  }
  return render(request, 'pages/components/forms.html', context)

@login_required(login_url="/accounts/login/")
def modals(request):
  context = {
    'parent': 'components',
    'segment': 'modals',
  }
  return render(request, 'pages/components/modals.html', context)

@login_required(login_url="/accounts/login/")
def typography(request):
  context = {
    'parent': 'components',
    'segment': 'typography',
  }
  return render(request, 'pages/components/typography.html', context)


# Authentication
from django.contrib import messages
from .forms import RegistrationForm

def register_view(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            
            form.save()
            return redirect('login')
        else:
            print("Registration failed!")
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        form = RegistrationForm()

    context = {'form': form}
    return render(request, 'accounts/sign-up.html', context)


class UserLoginView(LoginView):
  form_class = LoginForm
  template_name = 'accounts/sign-in.html'

@login_required
def password_change(request):
    if request.method == 'POST':
        form = UserPasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            form.save()
            return redirect('password_change_done')
    else:
        form = UserPasswordChangeForm(request.user)

    return render(request, 'accounts/password-change.html', {'form': form})

# Réinitialisation du mot de passe
def password_reset(request):
    if request.method == 'POST':
        form = UserPasswordResetForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            # Récupérer l'utilisateur associé à l'email
            User = get_user_model()  # Récupère le modèle utilisateur
            user = User.objects.get(email=email)
            print(user)   # Convertir le générateur en liste
            # Générer les paramètres uidb64 et token
            uidb64 = urlsafe_base64_encode(str(user.pk).encode())
            token = default_token_generator.make_token(user)
            reset_url = f"{request.scheme}://{get_current_site(request).domain}/accounts/password-reset-confirm/{uidb64}/{token}/"

            # Envoi de l'email de réinitialisation
            subject = 'Réinitialisation de mot de passe'
            message = f"Veuillez cliquer sur ce lien pour réinitialiser votre mot de passe: {reset_url}"
            send_mail(subject, message, 'no-reply@example.com', [email])

            return redirect('password_reset_done')
    else:
        form = UserPasswordResetForm()

    return render(request, 'accounts/forgot-password.html', {'form': form})
# Confirmer la réinitialisation du mot de passe
def password_reset_confirm(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = get_user_model().objects.get(pk=uid)
        if default_token_generator.check_token(user, token):
            if request.method == 'POST':
                form = UserSetPasswordForm(user, request.POST)
                if form.is_valid():
                    form.save()
                    return redirect('password_reset_complete')
            else:
                form = UserSetPasswordForm(user)
            return render(request, 'accounts/password_reset.html', {'form': form})
        else:
            return redirect('password_reset_invalid')
    except (TypeError, ValueError, OverflowError, get_user_model().DoesNotExist):
        return redirect('password_reset_invalid')

# Page après la réinitialisation du mot de passe
def password_reset_done(request):
    return render(request, 'accounts/password-reset-done.html')

# Page après la réinitialisation réussie
def password_reset_complete(request):
    return render(request, 'accounts/password_reset_complete.html')

def logout_view(request):
  logout(request)
  return redirect('/accounts/login/')

def lock(request):
  return render(request, 'accounts/lock.html')

# Errors
def error_404(request):
  return render(request, 'pages/404.html')

def error_500(request):
  return render(request, 'pages/examples/500.html')

# Extra
def upgrade_to_pro(request):
  return render(request, 'pages/upgrade-to-pro.html')