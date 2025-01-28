from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (CustomRegisterView, UserViewSet, EmployeeProfileViewSet, 
                        FournisseurViewSet, AbsenceViewSet,confirm_email, ResendConfirmationEmailView,
                    ForgotPasswordView,PasswordResetConfirmView)
from . import html
    


router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'employee-profiles', EmployeeProfileViewSet)
router.register(r'fournisseurs', FournisseurViewSet)
router.register(r'absences', AbsenceViewSet)

urlpatterns = [
    path('resend-confirmation/', ResendConfirmationEmailView.as_view(), name='resend_confirmation'),

    path('forgot-password/', ForgotPasswordView.as_view(), name='forgot_password'),
    path('reset-password/<uidb64>/<token>/', PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('register/', CustomRegisterView.as_view(), name='rest_register'),
    path('confirm-email/<str:token>/', confirm_email, name='confirm_email'),
    path('', include(router.urls)),




    path('employee-profile/', html.employee_profile_list, name='employee_profile_list'),
    path('employee-profile/print/', html.employee_profile_list_print, name='employee_profile_list_print'),
    path('employee-profile/export/', html.employee_profile_list_export, name='employee_profile_list_export'),
    path('employee-profile/update/<int:id>/', html.update_employee_profile, name='update_employee_profile'),
    path('employee-profiledelete/<int:id>/', html.delete_employee_profile, name='delete_employee_profile'),
    path('employee-profile/bulk-delete/', html.bulk_delete_employee_profile, name='bulk_delete_employee_profile'),


    path('user/', html.user_list, name='user_list'),
    path('user/delete/<uuid:id>/', html.delete_user, name='delete_user'),
    path('user/update/<uuid:id>/', html.update_user, name='update_user'),
    path('user/bulk_delete/', html.bulk_delete_users, name='bulk_delete_users'),

    path('fournisseur/', html.fournisseur_list, name='fournisseur_list'),
    path('fournisseur/print/', html.fournisseur_list_print, name='fournisseur_list_print'),
    path('fournisseur/export/', html.fournisseur_list_export, name='fournisseur_list_export'),
    path('fournisseur/update/<int:id>/', html.update_fournisseur, name='update_fournisseur'),
    path('fournisseur/delete/<int:id>/', html.delete_fournisseur, name='delete_fournisseur'),
    path('fournisseur/bulk-delete/', html.bulk_delete_fournisseur, name='bulk_delete_fournisseur'),
]
