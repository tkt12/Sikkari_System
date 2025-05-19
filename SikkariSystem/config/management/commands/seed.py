from django.core.management.base import BaseCommand
from django.utils.timezone import now
from apps.products.models import Department, Employee, Client, Product, Order, Inventory, Production

class Command(BaseCommand):
    help = 'データベースに初期データを投入する'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('シーダーを実行開始...'))

        # 部署データ
        departments = [
            Department.objects.get_or_create(id=1, name='社長'),
            Department.objects.get_or_create(id=2, name='営業部'),
            Department.objects.get_or_create(id=3, name='製造部'),
            Department.objects.get_or_create(id=4, name='製品管理部'),
            Department.objects.get_or_create(id=5, name='経理部'),
            Department.objects.get_or_create(id=6, name='人事部'),
        ]

        # 従業員データ
        employees = [
            Employee.objects.get_or_create(id='R0001', name='我仮 太郎', department=departments[0][0], password='1111rx'),
            Employee.objects.get_or_create(id='R0002', name='我仮 一郎', department=departments[1][0], password='2222ex'),
        ]

        # 得意先データ
        clients = [
            Client.objects.get_or_create(code='aa00011', name='株式会社AAA', phone='0000-0000-0000', address='大阪市西区', email='info@aaa.jp'),
            Client.objects.get_or_create(code='aa00012', name='株式会社BBB', phone='0000-0000-1111', address='大阪市中央区', email='info@bbb.net'),
        ]

        # 製品データ
        products = [
            Product.objects.get_or_create(code='xx0111', name='Type-A', price=1000),
            Product.objects.get_or_create(code='xx0222', name='Type-B', price=1200),
        ]

        # 受注データ
        orders = [
            Order.objects.get_or_create(client=clients[0][0], product=products[0][0], quantity=50, order_date=now(), delivery_date=now()),
        ]

        # 在庫データ
        inventories = [
            Inventory.objects.get_or_create(product=products[0][0], stock=50),
        ]

        # 生産データ
        productions = [
            Production.objects.get_or_create(product=products[0][0], batch_size=100, production_date=now()),
        ]

        self.stdout.write(self.style.SUCCESS('シーダー実行完了！'))
