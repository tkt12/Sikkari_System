# apps/products/admin.py

from django.contrib import admin
from .models import Product, Production, Inventory, StockMovement

### 製品管理の管理画面設定
# - 製品の一覧表示と詳細編集機能を提供
# - 検索機能とフィルタリング機能を実装
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('product_code', 'name', 'unit_price', 'created_at', 'updated_at')
    search_fields = ('product_code', 'name')
    ordering = ('product_code',)
    readonly_fields = ('created_at', 'updated_at')

### 生産管理の管理画面設定
# - 製造情報の一覧表示と詳細編集機能を提供
# - 日付による絞り込みと検索機能を実装
@admin.register(Production)
class ProductionAdmin(admin.ModelAdmin):
    list_display = (
        'manufacture_code', 
        'product', 
        'quantity',
        'order_date',
        'manufacture_deadline',
        'planned_completion_date',
        'completion_date'
    )
    list_filter = ('order_date', 'manufacture_deadline', 'completion_date')
    search_fields = ('manufacture_code', 'product__name', 'product__product_code')
    ordering = ('-order_date', 'manufacture_code')
    readonly_fields = ('created_at', 'updated_at')

### 在庫管理の管理画面設定
# - 在庫情報の一覧表示と詳細編集機能を提供
# - 在庫数による並び替えと検索機能を実装
@admin.register(Inventory)
class InventoryAdmin(admin.ModelAdmin):
    list_display = ('product', 'quantity', 'updated_at')
    search_fields = ('product__name', 'product__product_code')
    ordering = ('product__product_code',)
    readonly_fields = ('created_at', 'updated_at')

### 入出荷管理の管理画面設定
# - 入出荷履歴の一覧表示と詳細編集機能を提供
# - 入出荷種別と日付によるフィルタリングを実装
@admin.register(StockMovement)
class StockMovementAdmin(admin.ModelAdmin):
    list_display = (
        'movement_date',
        'product',
        'movement_type',
        'quantity',
        'note'
    )
    list_filter = ('movement_type', 'movement_date')
    search_fields = ('product__name', 'product__product_code', 'note')
    ordering = ('-movement_date', '-created_at')
    readonly_fields = ('created_at', 'updated_at')