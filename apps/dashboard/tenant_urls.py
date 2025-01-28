from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from django.conf.urls import handler404, handler500


handler404 = views.error_404
handler500 = views.error_500

urlpatterns = [
    # Index
    
   

    # Pages
    path('', views.dashboard, name="home"),
    path('dashboard/', views.dashboard, name="dashboard"),
    path('pages/transaction/', views.transaction, name="transaction"),
    path('pages/settings/', views.settings, name="settings"),

    # Tables
    path('tables/bs-tables/', views.bs_tables, name="bs_tables"),

    # Components
    path('components/buttons/', views.buttons, name="buttons"),
    path('components/notifications/', views.notifications, name="notifications"),
    path('components/forms/', views.forms, name="forms"),
    path('components/modals/', views.modals, name="modals"),
    path('components/typography/', views.typography, name="typography"),

    # Authentication
    path('accounts/register/', views.register_view, name="register"),
    path('accounts/login/', views.UserLoginView.as_view(), name="login"),
    path('accounts/logout/', views.logout_view, name="logout"),
    path('accounts/password-change/', views.password_change, name='password_change'),
    path('accounts/password-change-done/', views.password_reset_done, name="password_change_done"),
    path('accounts/password-reset/', views.password_reset, name="password_reset"),
    path('accounts/password-reset-confirm/<uidb64>/<token>/', views.password_reset_confirm, name="password_reset_confirm"),
    path('accounts/password-reset-done/', views.password_reset_done, name='password_reset_done'),
    path('accounts/password-reset-complete/', views.password_reset_complete, name='password_reset_complete'),

    path('accounts/lock/', views.lock, name="lock"),

    # Errors
    path('error/404/', views.error_404, name="error_404"),
    path('error/500/', views.error_500, name="error_500"),

    # Extra
    path('pages/upgrade-to-pro/', views.upgrade_to_pro, name="upgrade_to_pro"),
]
