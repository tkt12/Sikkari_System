# apps/sales/views.py

from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView
from django.urls import reverse_lazy
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import F, Sum, Count, FloatField, DecimalField   
from django.db.models.deletion import ProtectedError
from django.db.models.functions import TruncMonth, Coalesce
from django.shortcuts import redirect
from .models import Customer, Order, Product
from .forms import CustomerForm, OrderForm, ProductForm
from decimal import Decimal
import datetime

class HomeView(LoginRequiredMixin, TemplateView):
    """ホーム画面"""
    template_name = 'sales/home.html'

class CustomerListView(LoginRequiredMixin, ListView):
    """得意先一覧"""
    model = Customer
    template_name = 'sales/customer_list.html'
    context_object_name = 'customers'
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset()
        # 検索条件の取得
        code = self.request.GET.get('code')
        name = self.request.GET.get('name')
        
        # 検索条件による絞り込み
        if code:
            queryset = queryset.filter(customer_code__icontains=code)
        if name:
            queryset = queryset.filter(name__icontains=name)
        
        return queryset.order_by('customer_code')

from django.db.models import Sum, Avg, Count, Q

class CustomerDetailView(LoginRequiredMixin, DetailView):
    """得意先詳細"""
    model = Customer
    template_name = 'sales/customer_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        customer = self.object
        orders = customer.order_set.all()

        # 総受注金額を計算（NULLの場合は0として扱う）
        total_amount = orders.aggregate(
            total=Coalesce(
                Sum(
                    F('quantity') * F('product__unit_price'),
                    output_field=FloatField()
                ),
                Decimal('0')
            )
        )['total']

        # 平均受注金額を計算
        if orders.exists():
            average_amount = total_amount / orders.count()
        else:
            average_amount = 0

        # 未納品の受注件数
        undelivered_count = orders.filter(
            delivery_completed_date__isnull=True
        ).count()

        context.update({
            'total_amount': total_amount,
            'average_amount': average_amount,
            'undelivered_count': undelivered_count,
        })
        return context

class CustomerCreateView(LoginRequiredMixin, CreateView):
    """得意先登録"""
    model = Customer
    form_class = CustomerForm
    template_name = 'sales/customer_form.html'
    success_url = reverse_lazy('sales:customer_list')

    def form_valid(self, form):
        messages.success(self.request, '得意先を登録しました。')
        return super().form_valid(form)

class CustomerUpdateView(LoginRequiredMixin, UpdateView):
    """得意先更新"""
    model = Customer
    form_class = CustomerForm
    template_name = 'sales/customer_form.html'
    success_url = reverse_lazy('sales:customer_list')

    def form_valid(self, form):
        messages.success(self.request, '得意先情報を更新しました。')
        return super().form_valid(form)

class CustomerDeleteView(LoginRequiredMixin, DeleteView):
    """得意先削除"""
    model = Customer
    template_name = 'sales/customer_confirm_delete.html'
    success_url = reverse_lazy('sales:customer_list')

    def delete(self, request, *args, **kwargs):
        result = super().delete(request, *args, **kwargs)
        messages.success(self.request, "得意先を削除しました。")
        return result

    def post(self, request, *args, **kwargs):
        try:
            return self.delete(request, *args, **kwargs)
        except ProtectedError:
            messages.error(self.request, "関連する受注データが存在するため削除できません。")
            return redirect('sales:customer_detail', pk=self.get_object().pk)


class OrderListView(LoginRequiredMixin, ListView):
    """受注一覧"""
    model = Order
    template_name = 'sales/order_list.html'
    context_object_name = 'orders'
    paginate_by = 10
    ordering = ['-order_date', '-pk']

    def get_queryset(self):
        queryset = super().get_queryset()
        # 検索条件の取得
        customer = self.request.GET.get('customer')
        product = self.request.GET.get('product')
        
        # 検索条件による絞り込み
        if customer:
            queryset = queryset.filter(
                Q(customer__name__icontains=customer) |
                Q(customer__customer_code__icontains=customer)
            )
        if product:
            queryset = queryset.filter(
                Q(product__name__icontains=product) |
                Q(product__product_code__icontains=product)
            )
        
        return queryset

class OrderDetailView(LoginRequiredMixin, DetailView):
    """受注詳細"""
    model = Order
    template_name = 'sales/order_detail.html'

class OrderCreateView(LoginRequiredMixin, CreateView):
    """受注登録"""
    model = Order
    form_class = OrderForm
    template_name = 'sales/order_form.html'
    success_url = reverse_lazy('sales:order_list')

    def get_initial(self):
        initial = super().get_initial()
        # URLパラメータから得意先IDを取得
        customer_id = self.request.GET.get('customer')
        if customer_id:
            initial['customer'] = customer_id
        return initial

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, '受注を登録しました。')
        return response

class OrderUpdateView(LoginRequiredMixin, UpdateView):
    """受注更新"""
    model = Order
    form_class = OrderForm
    template_name = 'sales/order_form.html'

    def get_success_url(self):
        return reverse_lazy('sales:order_detail', kwargs={'pk': self.object.pk})

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, '受注情報を更新しました。')
        return response

class ProductListView(LoginRequiredMixin, ListView):
    """製品一覧"""
    model = Product
    template_name = 'sales/product_list.html'
    context_object_name = 'products'
    paginate_by = 10
    ordering = ['product_code']

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
        
        return queryset


class ProductDetailView(LoginRequiredMixin, DetailView):
    """製品詳細"""
    model = Product
    template_name = 'sales/product_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        product = self.object
        orders = product.order_set.all()

        # 総受注数と総受注金額を計算
        total_quantity = orders.aggregate(Sum('quantity'))['quantity__sum'] or 0
        total_amount = orders.aggregate(
            total=Sum(F('quantity') * F('product__unit_price'))
        )['total'] or 0

        context.update({
            'total_quantity': total_quantity,
            'total_amount': total_amount,
        })
        return context


class ProductCreateView(LoginRequiredMixin, CreateView):
    """製品登録"""
    model = Product
    form_class = ProductForm
    template_name = 'sales/product_form.html'
    success_url = reverse_lazy('sales:product_list')

    def form_valid(self, form):
        messages.success(self.request, '製品を登録しました。')
        return super().form_valid(form)


class ProductUpdateView(LoginRequiredMixin, UpdateView):
    """製品更新"""
    model = Product
    form_class = ProductForm
    template_name = 'sales/product_form.html'

    def get_success_url(self):
        return reverse_lazy('sales:product_detail', kwargs={'pk': self.object.pk})

    def form_valid(self, form):
        messages.success(self.request, '製品情報を更新しました。')
        return super().form_valid(form)


class ProductDeleteView(LoginRequiredMixin, DeleteView):
    """製品削除"""
    model = Product
    template_name = 'sales/product_confirm_delete.html'
    success_url = reverse_lazy('sales:product_list')

    def delete(self, request, *args, **kwargs):
        result = super().delete(request, *args, **kwargs)
        messages.success(self.request, "製品を削除しました。")
        return result

    def post(self, request, *args, **kwargs):
        try:
            return self.delete(request, *args, **kwargs)
        except ProtectedError:
            messages.error(self.request, "関連する受注データが存在するため削除できません。")
            return redirect('sales:product_detail', pk=self.get_object().pk)
        

class SalesReportView(LoginRequiredMixin, TemplateView):
    """売上管理"""
    template_name = 'sales/sales_report.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # 年月の取得（デフォルトは現在の年）
        selected_year = self.request.GET.get('year', datetime.datetime.now().year)
        try:
            selected_year = int(selected_year)
        except (TypeError, ValueError):
            selected_year = datetime.datetime.now().year

        # 得意先別月次データの取得
        monthly_data = Order.objects.filter(
            order_date__year=selected_year
        ).annotate(
            month=TruncMonth('order_date')
        ).values(
            'month',
            'customer__name'
        ).annotate(
            total_amount=Sum(F('quantity') * F('product__unit_price')),
            order_count=Count('id')
        ).order_by('customer__name', 'month')

        # 得意先別年間データの取得
        yearly_data = Order.objects.filter(
            order_date__year=selected_year
        ).values(
            'customer__name'
        ).annotate(
            total_amount=Sum(F('quantity') * F('product__unit_price')),
            order_count=Count('id')
        ).order_by('-total_amount')

        # 製品別データの取得
        product_data = Order.objects.filter(
            order_date__year=selected_year
        ).values(
            'product__name'
        ).annotate(
            total_amount=Sum(F('quantity') * F('product__unit_price')),
            total_quantity=Sum('quantity'),
            order_count=Count('id')
        ).order_by('-total_amount')

        # 月次合計の取得
        monthly_totals = Order.objects.filter(
            order_date__year=selected_year
        ).annotate(
            month=TruncMonth('order_date')
        ).values('month').annotate(
            total_amount=Sum(F('quantity') * F('product__unit_price')),
            order_count=Count('id')
        ).order_by('month')

        # 年間合計の取得
        yearly_total = Order.objects.filter(
            order_date__year=selected_year
        ).aggregate(
            total_amount=Sum(F('quantity') * F('product__unit_price'),
            output_field=DecimalField()),
            order_count=Count('id')
        )

        # 年のリストを作成（現在の年から過去3年分）
        current_year = datetime.datetime.now().year
        years = range(current_year - 3, current_year + 1)

        context.update({
            'selected_year': selected_year,
            'years': years,
            'monthly_data': monthly_data,
            'yearly_data': yearly_data,
            'product_data': product_data,
            'monthly_totals': monthly_totals,
            'yearly_total': yearly_total,
        })
        return context