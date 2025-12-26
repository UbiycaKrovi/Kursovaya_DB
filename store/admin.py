from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group
from .models import (
    User, Category, Supplier, Warehouse, Product, Review, 
    Cart, CartItem, Order, Payment, Delivery
)

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

class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0
    readonly_fields = ('get_total_price',)
    
    def get_total_price(self, obj):
        return f"{obj.product.price * obj.quantity} ₽"
    get_total_price.short_description = 'Сумма'
    
    def cart_user_email(self, obj):
        return obj.cart.user.email  
    cart_user_email.short_description = 'Почта'
    
    readonly_fields = ('get_total_price', 'cart_user_email')

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('user_display', 'items_count', 'total_price', 'created_at')
    list_filter = ('created_at',)
    inlines = [CartItemInline]
    readonly_fields = ('created_at',)
    
    def user_display(self, obj):
        return obj.user.email  
    user_display.short_description = 'Почта пользователя' 
    
    def items_count(self, obj):
        return obj.items.count()
    items_count.short_description = 'Товаров'
    
    def total_price(self, obj):
        return f"{obj.get_total_price()} ₽"
    total_price.short_description = 'Общая сумма'

class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0
    readonly_fields = ('get_total_price',)
    
    def get_total_price(self, obj):
        return f"{obj.product.price * obj.quantity} ₽"
    get_total_price.short_description = 'Сумма'
    
    def cart_user_email(self, obj):
        return obj.cart.user.email  
    cart_user_email.short_description = 'Почта'
    
    readonly_fields = ('get_total_price', 'cart_user_email')

admin.site.register(Category)
admin.site.register(Supplier)
admin.site.register(Warehouse)
admin.site.register(Product)
admin.site.register(Review)
admin.site.register(Order)
admin.site.register(Payment)
admin.site.register(Delivery)
admin.site.unregister(Group)