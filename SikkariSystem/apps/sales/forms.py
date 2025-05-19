from django import forms
from .models import Customer, Order, Product

class CustomerForm(forms.ModelForm):
    """得意先フォーム"""
    class Meta:
        model = Customer
        fields = ['customer_code', 'name', 'phone', 'postal_code', 'address', 'email']
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 全てのフィールドにform-controlクラスを追加
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'
            
        # 必須フィールドの設定
        self.fields['customer_code'].required = True
        self.fields['name'].required = True
        self.fields['phone'].required = True
        self.fields['postal_code'].required = True
        self.fields['address'].required = True
        self.fields['email'].required = True
        
        # プレースホルダーの設定
        self.fields['customer_code'].widget.attrs['placeholder'] = '例：AA00001'
        self.fields['name'].widget.attrs['placeholder'] = '例：株式会社シッカリ'
        self.fields['phone'].widget.attrs['placeholder'] = '例：06-1234-5678'
        self.fields['postal_code'].widget.attrs['placeholder'] = '例：123-4567'
        self.fields['address'].widget.attrs['placeholder'] = '例：大阪府大阪市中央区...'
        self.fields['email'].widget.attrs['placeholder'] = '例：info@example.com'
        
    def clean_customer_code(self):
        code = self.cleaned_data['customer_code']
        if not code.isalnum():  # 英数字のみ許可
            raise forms.ValidationError('得意先コードは英数字のみで入力してください。')
        return code
        
    def clean_phone(self):
        phone = self.cleaned_data['phone']
        # 電話番号フォーマットの簡易チェック
        if not any(c.isdigit() for c in phone):
            raise forms.ValidationError('電話番号の形式が正しくありません。')
        return phone
        
    def clean_postal_code(self):
        postal_code = self.cleaned_data['postal_code']
        # 郵便番号フォーマットのチェック
        if not postal_code.replace('-', '').isdigit():
            raise forms.ValidationError('郵便番号の形式が正しくありません。')
        return postal_code
    

class OrderForm(forms.ModelForm):
    """受注フォーム"""
    class Meta:
        model = Order
        fields = ['customer', 'product', 'quantity', 'order_date', 'delivery_date', 'delivery_completed_date']
        widgets = {
            'order_date': forms.DateInput(attrs={'type': 'date'}),
            'delivery_date': forms.DateInput(attrs={'type': 'date'}),
            'delivery_completed_date': forms.DateInput(attrs={'type': 'date'}),
        }
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 全てのフィールドにform-controlクラスを追加
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'
        
        # 必須フィールドの設定
        self.fields['customer'].required = True
        self.fields['product'].required = True
        self.fields['quantity'].required = True
        self.fields['order_date'].required = True
        self.fields['delivery_date'].required = True
        self.fields['delivery_completed_date'].required = False
        
        # 数量の最小値を設定
        self.fields['quantity'].widget.attrs['min'] = 1
        
        # 得意先が指定されている場合は選択済みにする
        customer_id = kwargs.get('initial', {}).get('customer')
        if customer_id:
            self.fields['customer'].initial = customer_id
            
    def clean_quantity(self):
        quantity = self.cleaned_data['quantity']
        if quantity <= 0:
            raise forms.ValidationError('数量は1以上を指定してください。')
        return quantity
        
    def clean(self):
        cleaned_data = super().clean()
        order_date = cleaned_data.get('order_date')
        delivery_date = cleaned_data.get('delivery_date')
        delivery_completed_date = cleaned_data.get('delivery_completed_date')
        
        if order_date and delivery_date and order_date > delivery_date:
            raise forms.ValidationError('納品予定日は受注日より後の日付を指定してください。')
            
        if delivery_completed_date and delivery_date and delivery_completed_date < delivery_date:
            raise forms.ValidationError('納品完了日は納品予定日より後の日付を指定してください。')
            
        return cleaned_data

class ProductForm(forms.ModelForm):
    """製品フォーム"""
    class Meta:
        model = Product
        fields = ['product_code', 'name', 'unit_price']
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 全てのフィールドにform-controlクラスを追加
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'
            
        # 必須フィールドの設定
        self.fields['product_code'].required = True
        self.fields['name'].required = True
        self.fields['unit_price'].required = True
        
        # プレースホルダーの設定
        self.fields['product_code'].widget.attrs['placeholder'] = '例：XX0001'
        self.fields['name'].widget.attrs['placeholder'] = '例：Type-A'
        self.fields['unit_price'].widget.attrs['placeholder'] = '例：1000'
        
        # 単価の最小値を設定
        self.fields['unit_price'].widget.attrs['min'] = 0
        
    def clean_product_code(self):
        code = self.cleaned_data['product_code']
        if not code.isalnum():  # 英数字のみ許可
            raise forms.ValidationError('製品コードは英数字のみで入力してください。')
        return code
        
    def clean_unit_price(self):
        price = self.cleaned_data['unit_price']
        if price < 0:
            raise forms.ValidationError('単価は0以上を指定してください。')
        return price