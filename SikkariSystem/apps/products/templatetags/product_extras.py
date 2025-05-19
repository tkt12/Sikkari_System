# apps/products/templatetags/product_extras.py

from django import template
from django.db.models import Sum, F
from datetime import datetime, timedelta

register = template.Library()

### 金額計算フィルター
# - 数値と単価から合計金額を計算
@register.filter
def multiply(value, arg):
    try:
        return value * arg
    except (TypeError, ValueError):
        return 0

### 遅延日数計算フィルター
# - 予定日と実際の完了日から遅延日数を計算
@register.filter
def delay_days(completion_date, planned_date):
    if not completion_date or not planned_date:
        return 0
    delta = completion_date - planned_date
    return delta.days if delta.days > 0 else 0

### 在庫状態判定フィルター
# - 在庫数から状態を判定（在庫切れ、僅少、通常）
@register.filter
def stock_status(quantity):
    if quantity == 0:
        return 'zero'
    elif quantity < 10:
        return 'low'
    return 'normal'

### 期限切れ判定フィルター
# - 製造期日から期限切れかを判定
@register.filter
def is_overdue(deadline_date):
    return deadline_date and deadline_date < datetime.now().date()

### 百分率計算フィルター
# - 2つの数値から百分率を計算
@register.filter
def percentage(value, total):
    try:
        return round((value / total) * 100, 1)
    except (TypeError, ValueError, ZeroDivisionError):
        return 0