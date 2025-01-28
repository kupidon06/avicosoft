from django.urls import path
from . import views
from . import html

urlpatterns = [
    path('templates/', views.template_list, name='template_list'),
    path('templates/print/', views.template_list_print, name='template_list_print'),
    path('templates/export/', views.template_list_export, name='template_list_export'),
    path('templates/update/<int:id>/', views.update_template, name='update_template'),
    path('templates/delete/<int:id>/', views.delete_template, name='delete_template'),
    path('templates/bulk-delete/', views.bulk_delete_templates, name='bulk_delete_templates'),

    path('company-profile/', views.profile_settings, name='company_profile_list'),
    path('render-page/<int:template_id>/', html.render_page, name='render_page'),
    path('company-profile/update/<int:id>/', views.update_company_profile, name='update_company_profile'),
    path('company-profile/delete/<int:id>/', views.delete_company_profile, name='delete_company_profile'),

    # Gestion des configurations de page
    
    path('page-config/update/<int:id>/', views.update_page_config, name='update_page_config'),
    path('page-config/delete/<int:id>/', views.delete_page_config, name='delete_page_config'),
]

