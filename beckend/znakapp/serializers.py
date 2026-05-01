from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Category, Sign, Quiz, QuizResult, BadgeProject

class UserSerializer(serializers.ModelSerializer):
    """Сериализатор пользователя"""
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'date_joined']

class CategorySerializer(serializers.ModelSerializer):
    """Сериализатор категории"""
    signs_count = serializers.IntegerField(source='signs.count', read_only=True)
    
    class Meta:
        model = Category
        fields = ['id', 'name', 'description', 'created_at', 'signs_count']

class SignSerializer(serializers.ModelSerializer):
    """Сериализатор знака"""
    category_name = serializers.CharField(source='category.name', read_only=True)
    creator_username = serializers.CharField(source='created_by.username', read_only=True)
    
    class Meta:
        model = Sign
        fields = [
            'id', 'name', 'description', 'image_url', 'sign_type',
            'category', 'category_name', 'created_by', 'creator_username',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_by', 'created_at', 'updated_at']

class QuizSerializer(serializers.ModelSerializer):
    """Сериализатор теста"""
    signs_count = serializers.IntegerField(source='signs.count', read_only=True)
    signs = SignSerializer(many=True, read_only=True)
    
    class Meta:
        model = Quiz
        fields = ['id', 'title', 'description', 'signs', 'signs_count', 'created_at']

class QuizResultSerializer(serializers.ModelSerializer):
    """Сериализатор результатов теста"""
    username = serializers.CharField(source='user.username', read_only=True)
    quiz_title = serializers.CharField(source='quiz.title', read_only=True)
    percentage = serializers.SerializerMethodField()
    
    class Meta:
        model = QuizResult
        fields = ['id', 'user', 'username', 'quiz', 'quiz_title', 
                  'score', 'total_questions', 'percentage', 'completed_at']
    
    def get_percentage(self, obj):
        """Вычисление процента правильных ответов"""
        return round((obj.score / obj.total_questions) * 100, 2) if obj.total_questions > 0 else 0

# ========== НОВЫЕ СЕРИАЛИЗАТОРЫ ДЛЯ КОНСТРУКТОРА ЗНАЧКОВ ==========
class BadgeProjectSerializer(serializers.ModelSerializer):
    """Сериализатор проекта значка"""
    username = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = BadgeProject
        fields = [
            'id', 'name', 'user', 'username', 'shape_type', 'diameter_mm',
            'orientation', 'shapes_data', 'preview_image', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'user', 'username', 'created_at', 'updated_at', 'preview_image']

class BadgeProjectCreateSerializer(serializers.ModelSerializer):
    """Сериализатор для создания проекта"""
    class Meta:
        model = BadgeProject
        fields = ['name', 'shape_type', 'diameter_mm', 'orientation', 'shapes_data']