from django.urls import path
from . import views

urlpatterns = [
    path('categories/', views.category_list, name='category_list'),
    path('categories/update/<int:id>/', views.update_category, name='update_category'),
    path('categories/delete/<int:id>/', views.delete_category, name='delete_category'),
    path('categories/bulk_delete/', views.bulk_delete_category, name='bulk_delete_category'),

    path('products/', views.product_list, name='product_list'),
    path('products/update/<int:id>/', views.update_product, name='update_product'),
    path('products/delete/<int:id>/', views.delete_product, name='delete_product'),
    path('products/bulk_delete/', views.bulk_delete_product, name='bulk_delete_product'),

    path('product_units/', views.product_unit_list, name='product_unit_list'),
    path('product_units/update/<int:id>/', views.update_product_unit, name='update_product_unit'),
    path('product_units/delete/<int:id>/', views.delete_product_unit, name='delete_product_unit'),
    path('product_units/bulk_delete/', views.bulk_delete_product_unit, name='bulk_delete_product_unit'),

    path('discounts/', views.discount_list, name='discount_list'),
    path('discounts/update/<int:id>/', views.update_discount, name='update_discount'),
    path('discounts/delete/<int:id>/', views.delete_discount, name='delete_discount'),
    path('discounts/bulk_delete/', views.bulk_delete_discount, name='bulk_delete_discount'),
]
