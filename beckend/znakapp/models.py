from django.db import models
from django.contrib.auth.models import User

class Category(models.Model):
    """Категория знаков"""
    name = models.CharField('Название', max_length=100)
    description = models.TextField('Описание', blank=True)
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)
    
    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'
    
    def __str__(self):
        return self.name

class Sign(models.Model):
    """Модель знака"""
    TYPE_CHOICES = [
        ('warning', 'Предупреждающий'),
        ('prohibitory', 'Запрещающий'),
        ('mandatory', 'Предписывающий'),
        ('information', 'Информационный'),
        ('service', 'Сервисный'),
    ]
    
    name = models.CharField('Название', max_length=200)
    description = models.TextField('Описание')
    image_url = models.URLField('URL изображения', blank=True)
    sign_type = models.CharField('Тип знака', max_length=20, choices=TYPE_CHOICES)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='signs', verbose_name='Категория')
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, verbose_name='Создал')
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)
    updated_at = models.DateTimeField('Дата обновления', auto_now=True)
    
    class Meta:
        verbose_name = 'Знак'
        verbose_name_plural = 'Знаки'
        ordering = ['name']
    
    def __str__(self):
        return self.name

class Quiz(models.Model):
    """Тест/викторина по знакам"""
    title = models.CharField('Название', max_length=200)
    description = models.TextField('Описание')
    signs = models.ManyToManyField(Sign, related_name='quizzes', verbose_name='Знаки в тесте')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Тест'
        verbose_name_plural = 'Тесты'
    
    def __str__(self):
        return self.title

class QuizResult(models.Model):
    """Результаты прохождения тестов"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='quiz_results')
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='results')
    score = models.IntegerField('Результат в баллах')
    total_questions = models.IntegerField('Всего вопросов')
    completed_at = models.DateTimeField('Дата завершения', auto_now_add=True)
    
    class Meta:
        verbose_name = 'Результат теста'
        verbose_name_plural = 'Результаты тестов'
    
    def __str__(self):
        return f"{self.user.username} - {self.quiz.title}: {self.score}/{self.total_questions}"

# ========== НОВАЯ МОДЕЛЬ ДЛЯ КОНСТРУКТОРА ЗНАЧКОВ ==========
class BadgeProject(models.Model):
    """Проект конструктора значков"""
    SHAPE_CHOICES = [
        ('circle', 'Круг'),
        ('square', 'Квадрат'),
        ('star', 'Звезда'),
        ('shield', 'Щит'),
        ('heart', 'Сердце'),
        ('oval', 'Овал'),
        ('hexagon', 'Шестиугольник'),
        ('cross', 'Крест'),
    ]
    
    ORIENTATION_CHOICES = [
        ('portrait', 'Портретная'),
        ('landscape', 'Альбомная'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='badge_projects', verbose_name='Пользователь')
    name = models.CharField('Название проекта', max_length=200, default='Мой значок')
    shape_type = models.CharField('Форма', max_length=20, choices=SHAPE_CHOICES, default='circle')
    diameter_mm = models.FloatField('Диаметр (мм)', default=44)
    orientation = models.CharField('Ориентация', max_length=10, choices=ORIENTATION_CHOICES, default='portrait')
    shapes_data = models.JSONField('Данные изображений', default=dict)
    preview_image = models.ImageField('Превью', upload_to='badge_previews/', null=True, blank=True)
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)
    updated_at = models.DateTimeField('Дата обновления', auto_now=True)
    
    class Meta:
        verbose_name = 'Проект значка'
        verbose_name_plural = 'Проекты значков'
        ordering = ['-updated_at']
    
    def __str__(self):
        return f"{self.name} - {self.user.username}"