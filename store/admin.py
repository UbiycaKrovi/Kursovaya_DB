from django.contrib import admin
from .models import User, Category, Supplier, Warehouse, Product, Cart, CartItem, Order, Payment, Delivery, Review

admin.site.register(User)
admin.site.register(Category)
admin.site.register(Supplier)
admin.site.register(Warehouse)
admin.site.register(Product)
admin.site.register(Cart)
admin.site.register(CartItem)
admin.site.register(Order)
admin.site.register(Payment)
admin.site.register(Delivery)
admin.site.register(Review)