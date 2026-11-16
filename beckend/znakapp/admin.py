from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.db.models import Count, Q
from django.utils import timezone
from datetime import timedelta
from .models import (Category, Sign, Quiz, QuizResult, BadgeProject,
                     SiteVisit, Feedback
)

admin.site.site_header = 'Админ-панель "Значки"'
admin.site.site_title = 'Значки'
admin.site.index_title = 'Управление сайтом'

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'created_at']
    search_fields = ['name']
    list_filter = ['created_at']

@admin.register(Sign)
class SignAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'sign_type', 'category', 'created_by', 'created_at']
    list_filter = ['sign_type', 'category', 'created_at']
    search_fields = ['name', 'description']
    raw_id_fields = ['category', 'created_by']

@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'created_at']
    filter_horizontal = ['signs']

@admin.register(QuizResult)
class QuizResultAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'quiz', 'score', 'total_questions', 'completed_at']
    list_filter = ['quiz', 'completed_at']

# ========== НОВАЯ АДМИНКА ДЛЯ КОНСТРУКТОРА ЗНАЧКОВ ==========
@admin.register(BadgeProject)
class BadgeProjectAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'user', 'shape_type', 'diameter_mm', 'orientation', 'created_at']
    list_filter = ['shape_type', 'orientation', 'created_at']
    search_fields = ['name', 'user__username']
    readonly_fields = ['created_at', 'updated_at']



@admin.register(SiteVisit)
class SiteVisitAdmin(admin.ModelAdmin):
    """Админка пдя просмотра посещений сайта"""

    list_display = [
        'created_at', 'is_mobile', 'user_link', 'path',
        'method', 'browser', 'os', 'device_icon', 'response_time_display'
    ]
    list_filter = [
        'method', 'is_mobile', 'browser', 'os', 'status_code',
        ('created_at', admin.DateFieldListFilter),
    ]
    search_fields = ['id_address', 'path', 'user_agent', 'user__username']
    readonly_fields = [
        'ip_address', 'user', 'path', 'method', 'user_agent',
        'referer', 'session_key', 'screen_resolution', 'language', 
        'country', 'city', 'is_mobile', 'browser', 'os', 'response_time_ms',
        'status_code', 'created_at'
    ]
    date_hierarchy = 'created_at'
    ordering = ['-created_at']
    list_per_page = 50

    fieldsets = (
        ('Основное', {
            'fields': ('ip_address', 'user', 'path', 'method', 'status_code')
        }),
        ('Устройство и браузер', {
            'fields': ('user_agent', 'browser', 'os', 'is_mobile',
                       'screen_resolution', 'lenguage')
        }),
        ('Источник', {
            'fields': ('referer', 'country', 'city')
        }),
        ('Производительность', {
            'fields': ('response_time_ms', 'created_at')
        }),
    )

    def has_add_permission(self, request):
        #Запрещаем создавыть посещения вручную
        return False

    def has_change_permission(self, request, obj = None):
        #Только просмотр
        return False
    @admin.display(description='IP')
    def short_ip(self, obj):
        return obj.ip_addres or '—'
    @admin.display(description='Пользователь')
    def user_link(self, obj):
        if obj.user:
            url = reverse('admin:auth_user_change', args=[obj.user.id])
            return format_html('<a href="{}">{}</a>', url, obj.user.username)
        return format_html('<span style="color:#999;">Аноним</span>')
    @admin.display(description='Устройство')
    def device_icon(self, obj):
        if obj.is_mobile:
            return format_html('<span title="Мобильное">📱</span>')
        return format_html('<span title="Десктоп">💻</span>')
    
    @admin.display(description='Время ответа')
    def response_time_display(self, obj):
        if obj.response_time_ms is None:
            return '—'
        if obj.response_time_ms < 200:
            color = 'green'
        elif obj.response_time_ms < 500:
            color = 'orange'
        else:
            color = 'red'
        return format_html(
            '<span style="color:{};">{} мс</span>',
            color, obj.response_time_ms
        )


@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    """Админка для обратной связи"""
    
    list_display = [
        'id', 'name', 'email', 'category_badge', 'subject',
        'status_badge', 'priority_badge', 'created_at'
    ]
    list_filter = [
        'status', 'priority', 'category',
        ('created_at', admin.DateFieldListFilter),
    ]
    search_fields = ['name', 'email', 'subject', 'message', 'phone']
    readonly_fields = [
        'user', 'name', 'email', 'phone', 'category', 'subject',
        'message', 'ip_address', 'user_agent',
        'created_at', 'updated_at', 'responded_at', 'responded_by'
    ]
    date_hierarchy = 'created_at'
    ordering = ['-created_at']
    list_per_page = 30
    
    fieldsets = (
        ('Отправитель', {
            'fields': ('user', 'name', 'email', 'phone')
        }),
        ('Сообщение', {
            'fields': ('category', 'subject', 'message')
        }),
        ('Метаданные', {
            'fields': ('ip_address', 'user_agent', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
        ('Обработка', {
            'fields': ('status', 'priority', 'admin_response',
                        'responded_at', 'responded_by')
        }),
    )
    
    actions = ['mark_in_progress', 'mark_resolved', 'mark_rejected']
    
    @admin.display(description='Категория')
    def category_badge(self, obj):
        colors = {
            'question': '#2196F3',
            'bug': '#f44336',
            'suggestion': '#4CAF50',
            'complaint': '#FF9800',
            'other': '#9E9E9E',
        }
        return format_html(
            '<span style="background:{}; color:white; padding:2px 8px; '
            'border-radius:10px; font-size:11px;">{}</span>',
            colors.get(obj.category, '#999'),
            obj.get_category_display()
        )
    
    @admin.display(description='Статус')
    def status_badge(self, obj):
        colors = {
            'new': '#f44336',
            'in_progress': '#FF9800',
            'resolved': '#4CAF50',
            'rejected': '#9E9E9E',
        }
        return format_html(
            '<span style="background:{}; color:white; padding:2px 8px; '
            'border-radius:10px; font-size:11px;">{}</span>',
            colors.get(obj.status, '#999'),
            obj.get_status_display()
        )
    
    @admin.display(description='Приоритет')
    def priority_badge(self, obj):
        icons = {
            'low': '🟢',
            'medium': '🟡',
            'high': '🟠',
            'critical': '🔴',
        }
        return format_html(
            '{} {}',
            icons.get(obj.priority, ''),
            obj.get_priority_display()
        )
    
    @admin.action(description='Отметить как «В обработке»')
    def mark_in_progress(self, request, queryset):
        updated = queryset.update(status='in_progress')
        self.message_user(request, f'Обновлено: {updated}')
    
    @admin.action(description='Отметить как «Решено»')
    def mark_resolved(self, request, queryset):
        updated = queryset.update(status='resolved')
        self.message_user(request, f'Обновлено: {updated}')
    
    @admin.action(description='Отметить как «Отклонено»')
    def mark_rejected(self, request, queryset):
        updated = queryset.update(status='rejected')
        self.message_user(request, f'Обновлено: {updated}')
    
    def save_model(self, request, obj, form, change):
        """При сохранении ответа админа — обновляем метаданные."""
        if obj.admin_response and not obj.responded_at:
            obj.responded_at = timezone.now()
            obj.responded_by = request.user
            if obj.status == 'new':
                obj.status = 'in_progress'
        super().save_model(request, obj, form, change)