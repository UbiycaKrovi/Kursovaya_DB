from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import *

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'role', 'phone', 'is_staff')
    list_filter = ('role', 'is_staff', 'is_active')
    fieldsets = UserAdmin.fieldsets + (
        ('Дополнительно', {'fields': ('role', 'phone', 'address')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Дополнительно', {'fields': ('role', 'phone', 'address')}),
    )

admin.site.register([Category, Supplier, Warehouse, Product, Cart, CartItem, 
                    Order, Payment, Delivery, Review])