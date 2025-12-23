from django.urls import path
from . import views

urlpatterns = [
    path('', views.product_list, name='product_list'),
    path('product/<int:pk>/', views.product_detail, name='product_detail'),
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('cart/', views.cart_view, name='cart'),
    path('add-to-cart/<int:pk>/', views.add_to_cart, name='add_to_cart'),
    path('remove-from-cart/<int:pk>/', views.remove_from_cart, name='remove_from_cart'),
    path('update-cart/<int:pk>/', views.update_cart_item, name='update_cart_item'),
    path('product/create/', views.ProductCreateView.as_view(), name='product_create'),
    
    # Корзина
    path('cart/', views.cart_view, name='cart'),
    path('cart/add/<int:pk>/', views.add_to_cart, name='add_to_cart'),
    path('cart/remove/<int:pk>/', views.remove_from_cart, name='remove_from_cart'),
    path('cart/update/<int:pk>/', views.update_cart_item, name='update_cart_item'),

    # Заказы
    path('cart/checkout/', views.checkout, name='checkout'),
    path('orders/', views.order_list, name='order_list'),
    path('orders/<int:pk>/', views.order_detail, name='order_detail'),

    # Товары поставщика
    path('supplier/<int:pk>/', views.supplier_products, name='supplier_products'),

    # Экспорт
    path('export/products/json/', views.export_products_json, name='export_products_json'),
    path('export/products/csv/', views.export_products_csv, name='export_products_csv'),
    path('export/orders/json/', views.export_orders_json, name='export_orders_json'),
    path('export/orders/csv/', views.export_orders_csv, name='export_orders_csv'),
    path('export/suppliers/json/', views.export_suppliers_json, name='export_suppliers_json'),
    path('export/suppliers/csv/', views.export_suppliers_csv, name='export_suppliers_csv'),
]