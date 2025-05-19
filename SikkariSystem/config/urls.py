from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from .views import HomeView

urlpatterns = [
    # ルートページ
    path('', HomeView.as_view(), name='home'),
    
    # 管理画面
    path('admin/', admin.site.urls),
    
    # サブシステム
    path('sales/', include('apps.sales.urls')),
    path('products/', include('apps.products.urls')),
    
    # 認証
    path('accounts/login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('accounts/logout/', auth_views.LogoutView.as_view(next_page='/accounts/login/'), name='logout'),
]