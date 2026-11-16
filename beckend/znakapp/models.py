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


# создаем админку самостоятельно
# ========== НОВЫЕ МОДЕЛИ ДЛЯ АНАЛИТИКИ И ОБРАТНОЙ СВЯЗИ ==========

class SiteVisit(models.Model):
    ''' модель посещения сайта'''
    ip_address = models.GenericIPAddressField('IP-адрес', null=True, blank=True)
    user = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name='visit', verbose_name='Пользователь'
    )
    path = models.CharField('Путь', max_length=500)
    method = models.CharField('HTTP метод', max_length=10, default='GET')
    user_agent = models.TextField('User-Agent', blank=True)
    referer =models.URLField('Источник перехода', max_length=500, blank=True)
    session_key = models.CharField('Ключ сессии', max_length=40, blank=True)
    screen_resolution = models.CharField('Разрешение эклана', max_length=20, blank=True)
    language = models.CharField('Язык браузера', max_length=20, blank=True)
    country = models.CharField('Страна', max_length=100, blank=True)
    city = models.CharField('Город', max_length=100, blank=True)
    is_mobile = models.BooleanField('Мобильное устройство', default=False)
    browser = models.CharField('Браузер', max_length=100, blank=True)
    os = models.CharField('ОС', max_length=100, blank=True)
    response_time_ms = models.IntegerField('Время ответа (мс)', null=True, blank=True)
    status_code = models.IntegerField('HTTP статус', null=True, blank=True)
    created_at = models.DateTimeField('Дата и время', auto_now_add=True, db_index=True)

    class Meta:
        verbose_name = 'Посещение'
        verbose_name_plural = 'Посещения'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['-created_at']),
            models.Index(fields=['ip_address']),
            models.Index(fields=['path']),
        ]

    def __str__(self):
        user_str = self.user.username if self.user else 'Ананим'
        return f"{user_str} - {self.path} ({self.created_at.strftime('%d.%m.%Y %H:%M')})"

class Feedback(models.Model):
    '''Модель обратной связи'''
    STATUS_CHOICES = [
        ('new', 'Новое'),
        ('in_progress', 'В обработке'),
        ('resolved', 'Решено'),
        ('rejected', 'Отклонено'),        # ← было 'rejectet'
    ]

    PRIORITY_CHOICES = [
        ('low', 'Низкий'),
        ('medium', 'Средний'),
        ('high', 'Высокий'),
        ('critical', 'Критический'),
    ]

    CATEGORY_CHOICES = [
        ('question', 'Вопрос'),
        ('bug', 'Ошибка'),
        ('suggestion', 'Предложение'),
        ('complaint', 'Жалоба'),
        ('other', 'Другое'),
    ]

    user = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='feedbacks', verbose_name='Пользователь'
    )
    name = models.CharField('Имя', max_length=100)
    email = models.EmailField('Email')
    phone = models.CharField('Телефон', max_length=20, blank=True)
    category = models.CharField('Категория', max_length=20,
                                choices=CATEGORY_CHOICES, default='question')
    priority = models.CharField('Приоритет', max_length=20,
                                choices=PRIORITY_CHOICES, default='medium')  # ← добавлено
    subject = models.CharField('Тема', max_length=200)
    message = models.TextField('Сообщение')
    status = models.CharField('Статус', max_length=20,
                              choices=STATUS_CHOICES, default='new')         # ← было 'medium'

    ip_address = models.GenericIPAddressField('IP-адрес', null=True, blank=True)
    user_agent = models.TextField('User-Agent', blank=True)

    admin_response = models.TextField('Ответ администратора', blank=True)
    responded_at = models.DateTimeField('Дата ответа', null=True, blank=True)
    responded_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='responded_feedbacks', verbose_name='Ответил'
    )

    created_at = models.DateTimeField('Дата создания', auto_now_add=True)
    updated_at = models.DateTimeField('Дата обновления', auto_now=True)

    class Meta:
        verbose_name = 'Обратная связь'
        verbose_name_plural = 'Обратная связь'      # ← было 'Обрантая связь'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} - {self.subject} ({self.get_status_display()})"