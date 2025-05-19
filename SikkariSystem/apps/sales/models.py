from django.db import models

class Customer(models.Model):
    """得意先モデル"""
    customer_code = models.CharField("得意先コード", max_length=10, unique=True)
    name = models.CharField("得意先名", max_length=100)
    phone = models.CharField("電話番号", max_length=15)
    postal_code = models.CharField("郵便番号", max_length=8)
    address = models.CharField("住所", max_length=200)
    email = models.EmailField("メールアドレス", max_length=254)
    created_at = models.DateTimeField("作成日時", auto_now_add=True)
    updated_at = models.DateTimeField("更新日時", auto_now=True)

    class Meta:
        verbose_name = "得意先"
        verbose_name_plural = "得意先一覧"

    def __str__(self):
        return f"{self.customer_code}: {self.name}"

class Product(models.Model):
    """製品モデル"""
    product_code = models.CharField("製品コード", max_length=10, unique=True)
    name = models.CharField("製品名", max_length=100)
    unit_price = models.DecimalField("製品単価", max_digits=10, decimal_places=0)
    created_at = models.DateTimeField("作成日時", auto_now_add=True)
    updated_at = models.DateTimeField("更新日時", auto_now=True)

    class Meta:
        verbose_name = "製品"
        verbose_name_plural = "製品一覧"

    def __str__(self):
        return f"{self.product_code}: {self.name}"

class Order(models.Model):
    """受注モデル"""
    customer = models.ForeignKey(
        Customer,
        on_delete=models.PROTECT,
        verbose_name="得意先"
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,
        verbose_name="製品"
    )
    quantity = models.IntegerField("受注数量")
    order_date = models.DateField("受注日")
    delivery_date = models.DateField("納品予定日")
    delivery_completed_date = models.DateField("納品完了日", null=True, blank=True)
    created_at = models.DateTimeField("作成日時", auto_now_add=True)
    updated_at = models.DateTimeField("更新日時", auto_now=True)

    class Meta:
        verbose_name = "受注"
        verbose_name_plural = "受注一覧"

    def __str__(self):
        return f"{self.customer.name} - {self.product.name} ({self.order_date})"

    @property
    def total_amount(self):
        """受注金額を計算"""
        return self.quantity * self.product.unit_price