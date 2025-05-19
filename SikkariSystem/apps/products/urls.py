# apps/products/urls.py

from django.urls import path
from . import views

### 製品管理システムのURLパターン定義
# 以下の機能に対するURLを提供:
# - 製品管理（一覧、詳細、登録、更新、削除）
# - 生産管理（一覧、詳細、登録、更新）
# - 在庫管理（一覧、詳細）
# - 入出荷管理（一覧、登録）
app_name = 'products'

urlpatterns = [
    # ホーム
    path('', views.HomeView.as_view(), name='home'),
    
    # 製品管理
    path('items/', views.ProductListView.as_view(), name='product_list'),
    path('items/<int:pk>/', views.ProductDetailView.as_view(), name='product_detail'),
    path('items/create/', views.ProductCreateView.as_view(), name='product_create'),
    path('items/<int:pk>/update/', views.ProductUpdateView.as_view(), name='product_update'),
    path('items/<int:pk>/delete/', views.ProductDeleteView.as_view(), name='product_delete'),
    
    # 生産管理
    path('production/', views.ProductionListView.as_view(), name='production_list'),
    path('production/<int:pk>/', views.ProductionDetailView.as_view(), name='production_detail'),
    path('production/create/', views.ProductionCreateView.as_view(), name='production_create'),
    path('production/<int:pk>/update/', views.ProductionUpdateView.as_view(), name='production_update'),
    path('production/history/', views.ProductionHistoryView.as_view(), name='production_history'),
    
    # 在庫管理
    path('inventory/', views.InventoryListView.as_view(), name='inventory_list'),
    path('inventory/<int:pk>/', views.InventoryDetailView.as_view(), name='inventory_detail'),
    
    # 入出荷管理
    path('stock/', views.StockMovementListView.as_view(), name='stock_list'),
    path('stock/inbound/create/', views.StockInboundCreateView.as_view(), name='stock_inbound_create'),
    path('stock/outbound/create/', views.StockOutboundCreateView.as_view(), name='stock_outbound_create'),
]