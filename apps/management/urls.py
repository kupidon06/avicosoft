from django.urls import path, include
from rest_framework.routers import DefaultRouter

from . import html



urlpatterns = [
   
    # URLs pour les Bâtiments
    path('building/', html.building_list, name='building_list'),
    path('building/print/', html.building_list_print, name='building_list_print'),
    path('building/export/', html.building_list_export, name='building_list_export'),
    path('building/update/<int:id>/', html.update_building, name='update_building'),
    path('building/delete/<int:id>/', html.delete_building, name='delete_building'),
    path('building/bulk-delete/', html.bulk_delete, name='bulk_delete'),

    # URLs pour les Races
    path('breed/', html.breed_list, name='breed_list'),
    path('breed/print/', html.breed_list_print, name='breed_list_print'),
    path('breed/export/', html.breed_list_export, name='breed_list_export'),
    path('breed/update/<int:id>/', html.update_breed, name='update_breed'),
    path('breed/delete/<int:id>/', html.delete_breed, name='delete_breed'),
    path('breed/bulk-delete/', html.bulk_delete_breed, name='bulk_delete_breeds'),

    # URLs pour les Batches
    path('batch/', html.batch_list, name='batch_list'),
    path('batch/update/<int:id>/', html.update_batch, name='update_batch'),
    path('batch/delete/<int:id>/', html.delete_batch, name='delete_batch'),
    path('batch/bulk-delete/', html.bulk_delete_batch, name='bulk_delete_batches'),

    # URLs pour les Aliments
    path('feed/', html.feed_list, name='feed_list'),
    path('feed/print/', html.feed_list_print, name='feed_list_print'),
    path('feed/export/', html.feed_list_export, name='feed_list_export'),
    path('feed/update/<int:id>/', html.update_feed, name='update_feed'),
    path('feed/delete/<int:id>/', html.delete_feed, name='delete_feed'),
    path('feed/bulk-delete/', html.bulk_delete_feed, name='bulk_delete_feeds'),

    #URLS pour les PERTES

    path('stock_loss/', html.stock_loss_list, name='stock_loss_list'),
    path('stock_loss/print/', html.stock_loss_list_print, name='stock_loss_list_print'),
    path('stock_loss/export/', html.stock_loss_export, name='stock_loss_export'),
    path('stock_loss/update/<int:id>/', html.update_stock_loss, name='update_stock_loss'),
    path('stock_loss/delete/<int:id>/', html.delete_stock_loss, name='delete_stock_loss'),
    path('stock_loss/bulk_delete/', html.bulk_delete_stock_loss, name='bulk_delete_stock_loss'),

    # URLs pour les Traitements
    path('treatment/', html.treatment_list, name='treatment_list'),
    path('treatment/print/', html.treatment_list_print, name='treatment_list_print'),
    path('treatment/export/', html.treatment_list_export, name='treatment_list_export'),
    path('treatment/update/<int:id>/', html.update_treatment, name='update_treatment'),
    path('treatment/delete/<int:id>/', html.delete_treatment, name='delete_treatment'),
    path('treatment/bulk-delete/', html.bulk_delete_treatment, name='bulk_delete_treatments'),

    # URLs pour les Journaux Quotidiens
    path('daily_logs/<int:batch_id>/', html.daily_log_list, name='daily_log_list'),
    path('daily_logs/<int:batch_id>/print/', html.daily_log_list_print, name='daily_log_list_print'),
    path('daily_logs/<int:batch_id>/export/', html.daily_log_list_export, name='daily_log_list_export'),
    path('daily_logs/update/<int:id>/', html.update_daily_log, name='update_daily_log'),
    path('daily_logs/delete/<int:id>/', html.delete_daily_log, name='delete_daily_log'),
    path('daily_logs/bulk-delete/', html.bulk_delete_daily_log, name='bulk_delete_daily_logs'),

    # URLs pour les Alimentations
    path('feeding/<int:batch_id>/', html.feeding_list, name='feeding_list'),
    path('feeding/<int:batch_id>/print/', html.feeding_list_print, name='feeding_list_print'),
    path('feeding/<int:batch_id>/export/', html.feeding_list_export, name='feeding_list_export'),
    path('feeding/update/<int:id>/', html.update_feeding, name='update_feeding'),
    path('feeding/delete/<int:id>/', html.delete_feeding, name='delete_feeding'),
    path('feeding/bulk-delete/', html.bulk_delete_feeding, name='bulk_delete_feedings'),

    # URLs pour les Collectes d'Œufs
    path('egg_collections/<int:batch_id>/', html.egg_collection_list, name='egg_collection_list'),
    path('egg_collections/<int:batch_id>/print/', html.egg_collection_list_print, name='egg_collection_list_print'),
    path('egg_collections/<int:batch_id>/export/', html.egg_collection_list_export, name='egg_collection_list_export'),
    path('egg_collections/update/<int:id>/', html.update_egg_collection, name='update_egg_collection'),
    path('egg_collections/delete/<int:id>/', html.delete_egg_collection, name='delete_egg_collection'),
    path('egg_collections/bulk-delete/', html.bulk_delete_egg_collection, name='bulk_delete_egg_collections'),

    # URLs pour les Historiques de Traitements
    path('treatment_history/<int:batch_id>/', html.treatment_history_list, name='treatment_history_list'),
    path('treatment_history/print/<int:batch_id>/', html.treatment_history_list_print, name='treatment_history_list_print'),
    path('treatment_history/export/<int:batch_id>/', html.treatment_history_list_export, name='treatment_history_list_export'),
    path('treatment_history/update/<int:id>/', html.update_treatment_history, name='update_treatment_history'),
    path('treatment_history/delete/<int:id>/', html.delete_treatment_history, name='delete_treatment_history'),
    path('treatment_history/bulk-delete/', html.bulk_delete_treatment_history, name='bulk_delete_treatment_histories'),

    # URLs pour les Provisions
    path('provision/', html.provision_list, name='provision_list'),
    path('provision/print/', html.provision_list_print, name='provision_list_print'),
    path('provision/export/', html.provision_list_export, name='provision_list_export'),
    path('provision/update/<int:id>/', html.update_provision, name='update_provision'),
    path('provision/delete/<int:id>/', html.delete_provision, name='delete_provision'),
    path('provision/bulk-delete/', html.bulk_delete_provision, name='bulk_delete_provisions'),

    # URLs pour les Catégories de Charges
    path('expense_category/', html.expense_category_list, name='expense_category_list'),
    path('expense_category/print/', html.expense_category_list_print, name='expense_category_list_print'),
    path('expense_category/export/', html.expense_category_list_export, name='expense_category_list_export'),
    path('expense_category/update/<int:id>/', html.update_expense_category, name='update_expense_category'),
    path('expense_category/delete/<int:id>/', html.delete_expense_category, name='delete_expense_category'),
    path('expense_category/bulk-delete/', html.bulk_delete_expense_categories, name='bulk_delete_expense_categories'),

    # URLs pour les Charges
    path('expense/', html.expense_list, name='expense_list'),
    path('expense/print/', html.expense_list_print, name='expense_list_print'),
    path('expense/export/', html.expense_list_export, name='expense_list_export'),
    path('expense/update/<int:id>/', html.update_expense, name='update_expense'),
    path('expense/delete/<int:id>/', html.delete_expense, name='delete_expense'),
    path('expense/bulk-delete/', html.bulk_delete_expenses, name='bulk_delete_expenses'),


    path('batch/allocations/<int:batch_id>/', html.batch_allocation_list, name='batch_allocation_list'),
    path('batch/allocations/delete/<int:id>/', html.delete_batch_allocation, name='delete_batch_allocation'),
    path('batch/allocations/bulk_delete/', html.bulk_delete_batch_allocation, name='bulk_delete_batch_allocations'),
    path('batch/allocations/export/<int:batch_id>/', html.batch_allocation_list_export, name='batch_allocation_list_export'),
    path('batch/allocations/print/<int:batch_id>/', html.batch_allocation_list_print, name='batch_allocation_list_print'),

    path('batch-statistics/', html.batch_statistics_view, name='batch-statistics'),
]
