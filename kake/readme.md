# settings.py

import os
from pathlib import Path
from datetime import timedelta

# Chemin de base du projet
BASE_DIR = Path(__file__).resolve().parent.parent

# Sécuriser la clé secrète en production
SECRET_KEY = 'django-insecure-s#=s_fa(l6+j=v78@^nt+t#i+y#)h33s^4)s9y!652ib&1_k7_'

DEBUG = True
MAIN_DOMAIN = "localhost"
SITE_ID = 1
ALLOWED_HOSTS = ['*']

# Applications partagées et spécifiques aux tenants
SHARED_APPS = (
    'django.contrib.contenttypes',
    'django.contrib.auth',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'apps.company',  # Application partagée pour les utilisateurs
)

TENANT_APPS = (
    'django.contrib.contenttypes',
    'django.contrib.auth',
    'django.contrib.sites',
    'django.contrib.sessions',
    'django.contrib.admin',
    'rest_framework',
    'rest_framework_simplejwt.token_blacklist',  # Pour les API REST
    'djoser',  # Pour l'authentification par API
    'drf_yasg',  # Pour la documentation de l'API
    'dj_rest_auth',  # Pour gérer l'authentification via API
    'allauth',  # Pour gérer l'authentification via différents services (Google, etc.)
    'allauth.account',  # Pour la gestion des comptes utilisateurs
    'allauth.socialaccount',  # Pour la gestion des comptes sociaux (Google OAuth2)
    'allauth.socialaccount.providers.google',  # Pour le provider Google OAuth2
    'rest_framework.authtoken',

    'apps.users',  # Application utilisateurs
    'apps.orders',  # Application commandes spécifique au tenant
    'apps.menus',  # Application menus spécifique au tenant
    'apps.delivery',  # Application livraison spécifique au tenant
    'apps.sales',  # Application ventes spécifique au tenant
)

# Routeur de base de données
DATABASE_ROUTERS = ['kake.router.TenantRouter']

# Middleware
MIDDLEWARE = [
    'kake.middleware.TenantMiddleware',  # Middleware multi-tenant
    'allauth.account.middleware.AccountMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# Modèles de tenant et de domaine
TENANT_MODEL = "company.Company"
DOMAIN_MODEL = 'company.Domain'

TENANT_PUBLIC_DOMAINS = ["localhost", "127.0.0.1"]

# URLConf
ROOT_URLCONF = 'TasteFlow.urls'

# Base de données
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': ,  # Nom de la base de données
        'USER':   # Utilisateur
        'PASSWORD':  # Mot de passe
        'HOST':   # Hôte
        'PORT': '5432',  # Port (par défaut PostgreSQL)
        'OPTIONS': {
            'sslmode': 'require',  # Mode SSL requis
        },
    }
}
# Configuration des applications installées
INSTALLED_APPS = [
    'kake',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    'django_filters',
    'rest_framework',
    'rest_framework_simplejwt.token_blacklist',
    'djoser',
    'drf_yasg',
    'dj_rest_auth',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google',
    'rest_framework.authtoken',
    'apps.company',
    'apps.users',
    'apps.orders',
    'apps.menus',
    'apps.delivery',
]

# REST Framework configuration
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 10,
}

REST_USE_JWT = True  # Activer JWT pour dj-rest-auth

# JWT Configuration
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=15),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),
    'ROTATE_REFRESH_TOKENS': False,
    'BLACKLIST_AFTER_ROTATION': True,
    'UPDATE_LAST_LOGIN': False,
    'AUTH_HEADER_TYPES': ('Bearer',),
}

# Utilisation de l'email comme identifiant principal pour l'authentification
AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend', 
    'allauth.account.auth_backends.AuthenticationBackend',
]

# Modèle utilisateur personnalisé
AUTH_USER_MODEL = 'users.User'

# Paramètres d'authentification
ACCOUNT_AUTHENTICATION_METHOD = 'email'
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_EMAIL_VERIFICATION = 'mandatory'
ACCOUNT_USERNAME_REQUIRED = False
ACCOUNT_EMAIL_CONFIRMATION_EXPIRE_DAYS = 3
ACCOUNT_EMAIL_CONFIRMATION_URL = 'account:confirm_email'

LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'
ACCOUNT_INACTIVE_REDIRECT_URL = '/account-inactive/'

SOCIAL_AUTH_GOOGLE_OAUTH2_KEY = 
SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET = 

# Cache
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
    }
}

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {'class': 'logging.StreamHandler'},
    },
    'root': {
        'handlers': ['console'],
        'level': 'DEBUG',
    },
}

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = ''
EMAIL_HOST_PASSWORD = ''

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = True

STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'static']

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
