from django.contrib import admin
from .models import Customer, Product, Order

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('customer_code', 'name', 'phone', 'address', 'created_at')
    search_fields = ('customer_code', 'name', 'phone', 'address')
    ordering = ('customer_code',)

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('product_code', 'name', 'unit_price', 'created_at')
    search_fields = ('product_code', 'name')
    ordering = ('product_code',)

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('customer', 'product', 'quantity', 'order_date', 'delivery_date', 'delivery_completed_date')
    list_filter = ('order_date', 'delivery_date', 'delivery_completed_date')
    search_fields = ('customer__name', 'product__name')
    ordering = ('-order_date',)