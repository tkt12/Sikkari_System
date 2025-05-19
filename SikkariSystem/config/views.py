from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin

class HomeView(LoginRequiredMixin, TemplateView):
    """トップページビュー
    
    システム全体のダッシュボード的な役割を果たし、
    各サブシステムへのリンクと概要を表示します。
    """
    template_name = 'home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # 各サブシステムの概要情報を取得
        context.update({
            'title': 'シッカリインダストリ株式会社',
            'subtitle': '生産販売管理システム',
        })
        return context