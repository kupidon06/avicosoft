from django.urls import path
from . import views

urlpatterns = [
    # Liste des compagnies
    path('companies/', views.company_list, name='company_list'),
    path('companies/print/', views.company_list_print, name='company_list_print'),
    path('companies/export/', views.company_list_export, name='company_list_export'),
    
    # Mise à jour d'une compagnie
    path('companies/update/<uuid:id>/', views.update_company, name='update_company'),
    
    # Suppression d'une compagnie
    path('companies/delete/<uuid:id>/', views.delete_company, name='delete_company'),
    
    # Suppression en masse
    path('companies/bulk_delete/', views.bulk_delete_companies, name='bulk_delete_companies'),
    
    # Liste des abonnements
    path('subscriptions/', views.subscription_list, name='subscription_list'),
    path('subscriptions/print/', views.subscription_list_print, name='subscription_list_print'),
    path('subscriptions/export/', views.subscription_list_export, name='subscription_list_export'),
    
    # Mise à jour d'un abonnement
    path('subscriptions/update/<uuid:id>/', views.update_subscription, name='update_subscription'),
    
    # Suppression d'un abonnement
    path('subscriptions/delete/<uuid:id>/', views.delete_subscription, name='delete_subscription'),
    
    # Liste des paiements
    path('payments/', views.payment_list, name='payment_list'),
    path('payments/print/', views.payment_list_print, name='payment_list_print'),
    path('payments/export/', views.payment_list_export, name='payment_list_export'),
    
    # Mise à jour d'un paiement
    path('payments/update/<uuid:id>/', views.update_payment, name='update_payment'),
    
    # Suppression d'un paiement
    path('payments/delete/<uuid:id>/', views.delete_payment, name='delete_payment'),
]
