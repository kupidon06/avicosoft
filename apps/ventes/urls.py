from django.urls import path
from .html import create_batch_allocation,user_order_list,product_list, apply_coupon, ecommerce ,filter_product_units, order_list, create_order, update_order, delete_order, export_orders, bulk_delete_orders, make_payment, create_order_without_user
from .test import initiate_payment,payment_webhook
urlpatterns = [
    path('pos/', product_list, name='pos'),
    path('ecommerce/',ecommerce , name='ecommerce'),
    path('apply_coupon/',apply_coupon , name='apply_coupon'),
    path('my-orders/',user_order_list , name='my-orders'),

    path('products/filter/', filter_product_units, name='filter_product_units'),
    path('orders/', order_list, name='order_list'),
    path('orders/bacthes/', create_batch_allocation, name='create_batch_allocation'),
    path('orders/create/', create_order, name='create_order'),
    path('orders/<uuid:order_id>/update/', update_order, name='update_order'),
    path('orders/<uuid:id>/delete/', delete_order, name='delete_order'),
    path('orders/export/', export_orders, name='order_list_export'),
    path('orders/bulk_delete/', bulk_delete_orders, name='bulk_delete_orders'),
    path('orders/<uuid:order_id>/payments/create/', make_payment, name='make_payment'),
    path('orders/create_without_user/', create_order_without_user, name='create_order_without_user'),
    path('payments/create/<uuid:order_id>/',initiate_payment, name='test_payment'),
    path('webhook/',payment_webhook, name='webhook')
]
