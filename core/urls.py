from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include,re_path
from apps.dashboard.html import index
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

# DRF-YASG Schema View Configuration
schema_view = get_schema_view(
    openapi.Info(
        title="AFB API",
        default_version='v1',
        description="Documentation for the API endpoints",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="support@example.com"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [



    # Dashboard
    path('', include('apps.dashboard.urls')),

    path('company/', include('apps.company.urls')),
    path('config/', include('apps.profile.urls')),
    # Products
    path('products/', include('apps.produits.urls')),

    # Management
    path('management/', include('apps.management.urls')),

    # Orders
    path('orders/', include('apps.ventes.urls')),

    # Users
    path('users/', include('apps.users.urls')),

    # Auth - JWT
    path('api/auth/login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/auth/verify/', TokenVerifyView.as_view(), name='token_verify'),

    # Allauth Endpoints
    path('auth/', include('allauth.urls')),

    # DRF-YASG
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
