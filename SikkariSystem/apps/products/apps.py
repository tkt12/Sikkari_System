# apps/products/apps.py

from django.apps import AppConfig

### 製品管理システムのアプリケーション設定
# - アプリケーションの基本設定を定義
# - 管理画面での表示名を設定
class ProductsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.products'
    verbose_name = '製品管理システム'