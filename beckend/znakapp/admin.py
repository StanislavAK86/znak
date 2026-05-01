from django.contrib import admin
from .models import Category, Sign, Quiz, QuizResult, BadgeProject

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