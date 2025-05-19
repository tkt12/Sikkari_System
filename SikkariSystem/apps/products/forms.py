# apps/products/forms.py

from django import forms
from .models import Product, Production, StockMovement

### 製品登録・編集フォーム
# - 製品情報の入力フォームを提供
# - 入力値の検証ルールを実装
class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['product_code', 'name', 'unit_price']
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 全フィールドにBootstrapのフォームクラスを適用
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'
            
        # 必須項目の設定
        self.fields['product_code'].required = True
        self.fields['name'].required = True
        self.fields['unit_price'].required = True
        
        # プレースホルダーの設定
        self.fields['product_code'].widget.attrs['placeholder'] = '例：P001'
        self.fields['name'].widget.attrs['placeholder'] = '例：標準部品A'
        self.fields['unit_price'].widget.attrs['placeholder'] = '例：1000'
        
    ### 製品コードのバリデーション
    # - 英数字のみ許可
    # - 重複チェック
    def clean_product_code(self):
        code = self.cleaned_data['product_code']
        if not code.isalnum():
            raise forms.ValidationError('製品コードは英数字のみで入力してください。')
        return code
        
    ### 単価のバリデーション
    # - 0以上の値のみ許可
    def clean_unit_price(self):
        price = self.cleaned_data['unit_price']
        if price < 0:
            raise forms.ValidationError('単価は0以上を指定してください。')
        return price

### 生産情報登録・編集フォーム
# - 製造情報の入力フォームを提供
# - 日付の整合性チェックを実装
class ProductionForm(forms.ModelForm):
    class Meta:
        model = Production
        fields = [
            'product', 
            'manufacture_code', 
            'quantity',
            'order_date',
            'manufacture_deadline',
            'planned_completion_date',
            'completion_date'
        ]
        widgets = {
            'order_date': forms.DateInput(attrs={'type': 'date'}),
            'manufacture_deadline': forms.DateInput(attrs={'type': 'date'}),
            'planned_completion_date': forms.DateInput(attrs={'type': 'date'}),
            'completion_date': forms.DateInput(attrs={'type': 'date'}),
        }
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 全フィールドにBootstrapのフォームクラスを適用
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'
            
        # 必須項目の設定
        self.fields['product'].required = True
        self.fields['manufacture_code'].required = True
        self.fields['quantity'].required = True
        self.fields['order_date'].required = True
        self.fields['manufacture_deadline'].required = True
        self.fields['planned_completion_date'].required = True
        
        # 製造数量の最小値を設定
        self.fields['quantity'].widget.attrs['min'] = 1
            
    ### フォーム全体のバリデーション
    # - 日付の整合性チェック
    def clean(self):
        cleaned_data = super().clean()
        order_date = cleaned_data.get('order_date')
        manufacture_deadline = cleaned_data.get('manufacture_deadline')
        planned_completion_date = cleaned_data.get('planned_completion_date')
        completion_date = cleaned_data.get('completion_date')
        
        if order_date and manufacture_deadline and manufacture_deadline < order_date:
            raise forms.ValidationError('製造期日は受注日より後の日付を指定してください。')
            
        if manufacture_deadline and planned_completion_date and planned_completion_date < manufacture_deadline:
            raise forms.ValidationError('完了予定日は製造期日より後の日付を指定してください。')
            
        if completion_date and planned_completion_date and completion_date < planned_completion_date:
            raise forms.ValidationError('完了日は完了予定日より後の日付を指定してください。')
            
        return cleaned_data

### 入出荷情報登録フォーム
# - 入出荷情報の入力フォームを提供
# - 在庫数のチェックを実装
class StockMovementForm(forms.ModelForm):
    class Meta:
        model = StockMovement
        fields = ['product', 'movement_type', 'quantity', 'movement_date', 'note']
        widgets = {
            'movement_date': forms.DateInput(attrs={'type': 'date'}),
        }
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 全フィールドにBootstrapのフォームクラスを適用
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'
            
        # 必須項目の設定
        self.fields['product'].required = True
        self.fields['movement_type'].required = True
        self.fields['quantity'].required = True
        self.fields['movement_date'].required = True
        
        # 数量の最小値を設定
        self.fields['quantity'].widget.attrs['min'] = 1
    
    ### 出荷時の在庫チェック
    # - 出荷の場合、在庫数を超える数量は指定できない
    def clean(self):
        cleaned_data = super().clean()
        product = cleaned_data.get('product')
        movement_type = cleaned_data.get('movement_type')
        quantity = cleaned_data.get('quantity')
        
        if product and movement_type == 'OUT' and quantity:
            try:
                inventory = product.inventory
                if quantity > inventory.quantity:
                    raise forms.ValidationError('出荷数量が在庫数を超えています。')
            except Product.inventory.RelatedObjectDoesNotExist:
                raise forms.ValidationError('この製品の在庫情報が存在しません。')