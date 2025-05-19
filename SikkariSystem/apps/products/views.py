# apps/products/views.py

from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.contrib import messages
from django.shortcuts import redirect
from django.db.models import Sum, F, FloatField
from django.db.models.functions import Coalesce
from .models import Product, Production, Inventory, StockMovement
from .forms import ProductForm, ProductionForm, StockMovementForm

### トップページビュー
# - 製品管理システムのダッシュボード的な役割
# - 各機能へのリンクと概要を表示

class HomeView(LoginRequiredMixin, TemplateView):
    """ホーム画面
    
    製品管理システムのダッシュボード的な役割を果たし、
    概要情報を表示します。
    """
    template_name = 'products/home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # 在庫金額の計算
        inventory_total = Inventory.objects.aggregate(
            total=Coalesce(
                Sum(
                    F('quantity') * F('product__unit_price'),
                    output_field=FloatField()
                ),
                0.0
            )
        )['total']
        
        # 概要情報を取得
        context.update({
            'product_count': Product.objects.count(),
            'production_ongoing': Production.objects.filter(completion_date__isnull=True).count(),
            'inventory_total': inventory_total,
        })
        return context

### 製品管理関連のビュー
# - 製品の一覧、詳細、登録、更新、削除機能を提供
class ProductListView(LoginRequiredMixin, ListView):
    """製品一覧"""
    model = Product
    template_name = 'products/product_list.html'
    context_object_name = 'products'
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset()
        # 検索条件の取得
        code = self.request.GET.get('code')
        name = self.request.GET.get('name')
        
        # 検索条件による絞り込み
        if code:
            queryset = queryset.filter(product_code__icontains=code)
        if name:
            queryset = queryset.filter(name__icontains=name)
        
        return queryset.order_by('product_code')

class ProductDetailView(LoginRequiredMixin, DetailView):
    """製品詳細"""
    model = Product
    template_name = 'products/product_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        product = self.object
        
        # 在庫情報の取得
        try:
            inventory = product.inventory
            context['inventory'] = inventory
        except Product.inventory.RelatedObjectDoesNotExist:
            context['inventory'] = None
        
        # 生産情報の取得
        context['productions'] = Production.objects.filter(
            product=product
        ).order_by('-order_date')[:5]
        
        # 入出荷履歴の取得
        context['stock_movements'] = StockMovement.objects.filter(
            product=product
        ).order_by('-movement_date')[:5]
        
        return context

class ProductCreateView(LoginRequiredMixin, CreateView):
    """製品登録"""
    model = Product
    form_class = ProductForm
    template_name = 'products/product_form.html'
    success_url = reverse_lazy('products:product_list')

    def form_valid(self, form):
        messages.success(self.request, '製品を登録しました。')
        return super().form_valid(form)

class ProductUpdateView(LoginRequiredMixin, UpdateView):
    """製品更新"""
    model = Product
    form_class = ProductForm
    template_name = 'products/product_form.html'

    def get_success_url(self):
        return reverse_lazy('products:product_detail', kwargs={'pk': self.object.pk})

    def form_valid(self, form):
        messages.success(self.request, '製品情報を更新しました。')
        return super().form_valid(form)

class ProductDeleteView(LoginRequiredMixin, DeleteView):
    """製品削除"""
    model = Product
    template_name = 'products/product_confirm_delete.html'
    success_url = reverse_lazy('products:product_list')

    def delete(self, request, *args, **kwargs):
        try:
            result = super().delete(request, *args, **kwargs)
            messages.success(self.request, "製品を削除しました。")
            return result
        except Exception as e:
            messages.error(self.request, "関連データが存在するため削除できません。")
            return redirect('products:product_detail', pk=self.get_object().pk)

### 生産管理関連のビュー
# - 生産情報の一覧、詳細、登録、更新機能を提供
class ProductionListView(LoginRequiredMixin, ListView):
    """生産情報一覧"""
    model = Production
    template_name = 'products/production_list.html'
    context_object_name = 'productions'
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset()
        # 未完了の生産情報のみを表示
        return queryset.filter(
            completion_date__isnull=True
        ).order_by('manufacture_deadline')

class ProductionDetailView(LoginRequiredMixin, DetailView):
    """生産情報詳細"""
    model = Production
    template_name = 'products/production_detail.html'

class ProductionCreateView(LoginRequiredMixin, CreateView):
    """生産情報登録"""
    model = Production
    form_class = ProductionForm
    template_name = 'products/production_form.html'
    success_url = reverse_lazy('products:production_list')

    def form_valid(self, form):
        messages.success(self.request, '生産情報を登録しました。')
        return super().form_valid(form)

class ProductionUpdateView(LoginRequiredMixin, UpdateView):
    """生産情報更新"""
    model = Production
    form_class = ProductionForm
    template_name = 'products/production_form.html'

    def get_success_url(self):
        return reverse_lazy('products:production_detail', kwargs={'pk': self.object.pk})

    def form_valid(self, form):
        messages.success(self.request, '生産情報を更新しました。')
        return super().form_valid(form)

class ProductionHistoryView(LoginRequiredMixin, ListView):
    """生産履歴"""
    model = Production
    template_name = 'products/production_history.html'
    context_object_name = 'productions'
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset()
        # 完了済みの生産情報のみを表示
        return queryset.filter(
            completion_date__isnull=False
        ).order_by('-completion_date')

### 在庫管理関連のビュー
# - 在庫情報の一覧と詳細表示機能を提供
class InventoryListView(LoginRequiredMixin, ListView):
    """在庫一覧"""
    model = Inventory
    template_name = 'products/inventory_list.html'
    context_object_name = 'inventories'
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset()
        # 検索条件の取得
        code = self.request.GET.get('code')
        name = self.request.GET.get('name')
        
        # 検索条件による絞り込み
        if code:
            queryset = queryset.filter(product__product_code__icontains=code)
        if name:
            queryset = queryset.filter(product__name__icontains=name)
        
        return queryset.order_by('product__product_code')

class InventoryDetailView(LoginRequiredMixin, DetailView):
    """在庫詳細"""
    model = Inventory
    template_name = 'products/inventory_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        inventory = self.object
        
        # 入出荷履歴の取得
        context['movements'] = StockMovement.objects.filter(
            product=inventory.product
        ).order_by('-movement_date')[:10]
        
        return context

### 入出荷管理関連のビュー
# - 入出荷履歴の一覧表示と登録機能を提供
class StockMovementListView(LoginRequiredMixin, ListView):
    """入出荷履歴一覧"""
    model = StockMovement
    template_name = 'products/stock_movement_list.html'
    context_object_name = 'movements'
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset()
        # 検索条件による絞り込み
        return queryset.order_by('-movement_date', '-created_at')

class StockInboundCreateView(LoginRequiredMixin, CreateView):
    """入荷登録"""
    model = StockMovement
    form_class = StockMovementForm
    template_name = 'products/stock_movement_form.html'
    success_url = reverse_lazy('products:stock_list')

    def get_initial(self):
        return {'movement_type': 'IN'}

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['movement_type'] = '入荷'
        return context

    def form_valid(self, form):
        messages.success(self.request, '入荷情報を登録しました。')
        return super().form_valid(form)

class StockOutboundCreateView(LoginRequiredMixin, CreateView):
    """出荷登録"""
    model = StockMovement
    form_class = StockMovementForm
    template_name = 'products/stock_movement_form.html'
    success_url = reverse_lazy('products:stock_list')

    def get_initial(self):
        return {'movement_type': 'OUT'}

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['movement_type'] = '出荷'
        return context

    def form_valid(self, form):
        messages.success(self.request, '出荷情報を登録しました。')
        return super().form_valid(form)