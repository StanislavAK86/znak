"""
Создаём кастомную страницу дашборда в админке
Создайте файл znakapp/admin_dashboard.py:
Кастомная страница дашборда в Django Admin.
Доступна по адресу /admin/dashboard/
"""

from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render
from django.db.models import Count
from django.utils import timezone
from datetime import timedelta
from .models import SiteVisit, Feedback, User, BadgeProject


@staff_member_required
def dashboard_view(request):
    """Главная страница дашборда"""
    now = timezone.now()
    today = now.replace(hour=0, minute=0, second=0, microsecond=0)
    week_ago = now - timedelta(days=7)
    month_ago = now - timedelta(days=30)
    
    # Статистика
    stats = {
        'visits_today': SiteVisit.objects.filter(created_at__gte=today).count(),
        'visits_week': SiteVisit.objects.filter(created_at__gte=week_ago).count(),
        'visits_month': SiteVisit.objects.filter(created_at__gte=month_ago).count(),
        'visits_total': SiteVisit.objects.count(),
        
        'unique_today': SiteVisit.objects.filter(
            created_at__gte=today
        ).values('ip_address').distinct().count(),
        
        'users_total': User.objects.count(),
        'users_today': User.objects.filter(date_joined__gte=today).count(),
        
        'feedback_new': Feedback.objects.filter(status='new').count(),
        'feedback_total': Feedback.objects.count(),
        
        'projects_total': BadgeProject.objects.count(),
    }
    
    # График за 7 дней
    visits_by_day = []
    for i in range(7):
        day_start = today - timedelta(days=6-i)
        day_end = day_start + timedelta(days=1)
        count = SiteVisit.objects.filter(
            created_at__gte=day_start,
            created_at__lt=day_end
        ).count()
        visits_by_day.append({
            'date': day_start.strftime('%d.%m'),
            'count': count
        })
    
    # Топ страниц
    top_pages = SiteVisit.objects.filter(
        created_at__gte=week_ago
    ).values('path').annotate(
        count=Count('id')
    ).order_by('-count')[:10]
    
    # Последние сообщения
    recent_feedback = Feedback.objects.order_by('-created_at')[:5]
    
    context = {
        'stats': stats,
        'visits_by_day': visits_by_day,
        'top_pages': top_pages,
        'recent_feedback': recent_feedback,
        'title': 'Дашборд',
    }
    
    return render(request, 'admin/dashboard.html', context)