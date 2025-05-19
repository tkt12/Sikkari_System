# apps/products/models.py

from django.db import models
from django.core.validators import MinValueValidator
from datetime import datetime, timedelta

### 製品モデル
# - 製品の基本情報を管理するモデル
# - 製品コード、製品名、単価などの基本属性を保持
# - 他のモデルから参照される中心的なモデル
class Product(models.Model):
    # 製品を一意に識別するコード
    product_code = models.CharField(
        "製品コード", 
        max_length=10, 
        unique=True
    )
    
    # 製品の表示名
    name = models.CharField(
        "製品名", 
        max_length=100
    )
    
    # 製品の販売単価（税抜）
    unit_price = models.DecimalField(
        "製品単価", 
        max_digits=10, 
        decimal_places=0
    )
    
    # レコードの作成日時と更新日時
    created_at = models.DateTimeField("作成日時", auto_now_add=True)
    updated_at = models.DateTimeField("更新日時", auto_now=True)

    class Meta:
        verbose_name = "製品"
        verbose_name_plural = "製品一覧"

    def __str__(self):
        return f"{self.product_code}: {self.name}"

    @property
    def current_stock(self):
        """現在の在庫数を取得"""
        try:
            return self.inventory.quantity
        except Inventory.DoesNotExist:
            return 0

    @property
    def stock_value(self):
        """在庫金額を計算"""
        return self.current_stock * self.unit_price

    def get_ongoing_productions(self):
        """製造中の生産情報を取得"""
        return self.production_set.filter(completion_date__isnull=True)

### 生産管理モデル
# - 製品の製造情報を管理するモデル
# - 製造工程の計画と実績を記録
# - 製造コード、数量、各種日付情報を管理
class Production(models.Model):
    # 製造対象の製品への参照
    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,  # 製品が削除されても製造記録は保持
        verbose_name="製品"
    )
    
    # 製造ロットを識別するコード
    manufacture_code = models.CharField(
        "製造コード", 
        max_length=20, 
        unique=True
    )
    
    # 製造予定数量（最小値1を保証）
    quantity = models.IntegerField(
        "製造数量",
        validators=[MinValueValidator(1)]
    )
    
    # 製造関連の日付情報
    order_date = models.DateField("受注日")
    manufacture_deadline = models.DateField("製造期日")
    planned_completion_date = models.DateField("完了予定日")
    completion_date = models.DateField("完了日", null=True, blank=True)
    
    # レコードの作成日時と更新日時
    created_at = models.DateTimeField("作成日時", auto_now_add=True)
    updated_at = models.DateTimeField("更新日時", auto_now=True)

    class Meta:
        verbose_name = "生産情報"
        verbose_name_plural = "生産情報一覧"

    def __str__(self):
        return f"{self.manufacture_code}: {self.product.name}"

    @property
    def is_completed(self):
        """製造完了状態を確認"""
        return bool(self.completion_date)

    @property
    def is_overdue(self):
        """期限切れ状態を確認"""
        if not self.completion_date and self.manufacture_deadline:
            return self.manufacture_deadline < datetime.now().date()
        return False

    @property
    def delay_days(self):
        """遅延日数を計算"""
        if self.completion_date and self.planned_completion_date:
            if self.completion_date > self.planned_completion_date:
                return (self.completion_date - self.planned_completion_date).days
        return 0

### 在庫管理モデル
# - 製品ごとの在庫数量を管理するモデル
# - 製品との1対1の関係を持つ
# - 入出荷時に自動的に更新される
class Inventory(models.Model):
    # 在庫を管理する製品への参照（1対1関係）
    product = models.OneToOneField(
        Product,
        on_delete=models.PROTECT,  # 製品が削除されても在庫記録は保持
        verbose_name="製品"
    )
    
    # 現在の在庫数量（負の値は許可しない）
    quantity = models.IntegerField(
        "在庫数",
        default=0,
        validators=[MinValueValidator(0)]
    )
    
    # レコードの作成日時と更新日時
    created_at = models.DateTimeField("作成日時", auto_now_add=True)
    updated_at = models.DateTimeField("更新日時", auto_now=True)

    class Meta:
        verbose_name = "在庫"
        verbose_name_plural = "在庫一覧"

    def __str__(self):
        return f"{self.product.name}: {self.quantity}"

    @property
    def total_value(self):
        """在庫金額を計算"""
        return self.quantity * self.product.unit_price

    @property
    def stock_status(self):
        """在庫状態を判定"""
        if self.quantity == 0:
            return 'zero'
        elif self.quantity < 10:
            return 'low'
        return 'normal'

    def get_recent_movements(self, days=30):
        """直近の入出荷履歴を取得"""
        start_date = datetime.now().date() - timedelta(days=days)
        return StockMovement.objects.filter(
            product=self.product,
            movement_date__gte=start_date
        ).order_by('-movement_date')

### 入出荷管理モデル
# - 製品の入出荷履歴を管理するモデル
# - 在庫の増減を記録し、Inventoryモデルと連動
# - 入荷/出荷の区別、日付、数量を管理
class StockMovement(models.Model):
    # 入出荷の種別を定義
    MOVEMENT_TYPE_CHOICES = [
        ('IN', '入荷'),
        ('OUT', '出荷'),
    ]

    # 入出荷対象の製品への参照
    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,  # 製品が削除されても入出荷記録は保持
        verbose_name="製品"
    )
    
    # 入荷か出荷かを示す区分
    movement_type = models.CharField(
        "移動タイプ",
        max_length=3,
        choices=MOVEMENT_TYPE_CHOICES
    )
    
    # 入出荷の数量（最小値1を保証）
    quantity = models.IntegerField(
        "数量",
        validators=[MinValueValidator(1)]
    )
    
    # 入出荷が行われた日付
    movement_date = models.DateField("入出荷日")
    
    # 補足情報
    note = models.TextField("備考", blank=True)
    
    # レコードの作成日時と更新日時
    created_at = models.DateTimeField("作成日時", auto_now_add=True)
    updated_at = models.DateTimeField("更新日時", auto_now=True)

    class Meta:
        verbose_name = "入出荷"
        verbose_name_plural = "入出荷一覧"
        ordering = ['-movement_date', '-created_at']  # デフォルトの並び順を設定

    def __str__(self):
        movement_type_str = "入荷" if self.movement_type == "IN" else "出荷"
        return f"{self.product.name}: {movement_type_str} ({self.quantity}個)"

    @classmethod
    def get_monthly_totals(cls, year=None, month=None):
        """月別の入出荷集計を取得"""
        from django.db.models import Sum
        from django.db.models.functions import TruncMonth

        # 年月が指定されていない場合は現在の年月を使用
        if year is None or month is None:
            today = datetime.now()
            year = today.year
            month = today.month

        start_date = datetime(year, month, 1)
        end_date = (start_date + timedelta(days=32)).replace(day=1)

        return cls.objects.filter(
            movement_date__range=(start_date, end_date - timedelta(days=1))
        ).values('movement_type').annotate(
            total_quantity=Sum('quantity')
        )

    ### 在庫数を自動的に更新するメソッド
    # - 新規の入出荷記録が作成される際に在庫数を更新
    # - 入荷の場合は在庫を増やし、出荷の場合は減らす
    # - 対象製品の在庫レコードが存在しない場合は新規作成
    def save(self, *args, **kwargs):
        # 出荷時の在庫チェック
        if self.movement_type == 'OUT':
            inventory = Inventory.objects.get_or_create(product=self.product)[0]
            if not self.pk and inventory.quantity < self.quantity:
                raise ValueError("出荷数量が在庫数を超えています。")

        # 在庫レコードを取得または作成
        inventory, _ = Inventory.objects.get_or_create(product=self.product)
        
        # 新規作成時のみ在庫を更新
        if not self.pk:  # pkがNoneの場合は新規作成
            if self.movement_type == 'IN':
                inventory.quantity += self.quantity  # 入荷時は在庫増
            else:
                inventory.quantity -= self.quantity  # 出荷時は在庫減
            inventory.save()
            
        super().save(*args, **kwargs)