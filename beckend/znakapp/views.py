from django.shortcuts import render
from rest_framework import generics, permissions, status, filters
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.contrib.auth.models import User
from django.db.models import Count, Q
from .models import Category, Sign, Quiz, QuizResult, BadgeProject, SiteVisit, Feedback
from django.http import HttpResponse
from .serializers import (
    UserSerializer, CategorySerializer, SignSerializer,
    QuizSerializer, QuizResultSerializer,
    BadgeProjectSerializer, BadgeProjectCreateSerializer,
    SiteVisitSerializer, FeedbackSerializer, FeedbackCreateSerializer
)
import base64
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.units import mm
from PIL import Image
import math
from rest_framework_simplejwt.tokens import RefreshToken
from django.utils import timezone
from datetime import timedelta


# ========== ПОЛЬЗОВАТЕЛИ ==========
class UserList(generics.ListAPIView):
    """Список всех пользователей"""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]


class UserDetail(generics.RetrieveAPIView):
    """Детальная информация о пользователе"""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]


@api_view(['GET', 'PUT'])
@permission_classes([IsAuthenticated])
def user_profile(request):
    """Получить или обновить профиль текущего пользователя"""
    user = request.user
    if request.method == 'GET':
        serializer = UserSerializer(user)
        return Response(serializer.data)

    elif request.method == 'PUT':
        serializer = UserSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ========== РЕГИСТРАЦИЯ ==========
class RegisterView(generics.CreateAPIView):
    """Регистрация нового пользователя"""
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        email = request.data.get('email', '')

        if not username or not password:
            return Response(
                {'error': 'Имя пользователя и пароль обязательны'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if User.objects.filter(username=username).exists():
            return Response(
                {'error': 'Пользователь с таким именем уже существует'},
                status=status.HTTP_400_BAD_REQUEST
            )

        user = User.objects.create_user(
            username=username,
            password=password,
            email=email
        )

        refresh = RefreshToken.for_user(user)

        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email
            }
        }, status=status.HTTP_201_CREATED)


# ========== КАТЕГОРИИ ==========
class CategoryList(generics.ListCreateAPIView):
    """Список категорий и создание новой"""
    queryset = Category.objects.annotate(signs_count=Count('signs'))
    serializer_class = CategorySerializer

    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAuthenticated()]
        return [AllowAny()]


class CategoryDetail(generics.RetrieveUpdateDestroyAPIView):
    """Детали, обновление и удаление категории"""
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]
        return [IsAuthenticated()]


# ========== ЗНАКИ ==========
class SignList(generics.ListCreateAPIView):
    """Список знаков и создание нового"""
    queryset = Sign.objects.select_related('category', 'created_by').all()
    serializer_class = SignSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at', 'sign_type']

    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAuthenticated()]
        return [AllowAny()]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    def get_queryset(self):
        queryset = super().get_queryset()

        sign_type = self.request.query_params.get('type')
        if sign_type:
            queryset = queryset.filter(sign_type=sign_type)

        category_id = self.request.query_params.get('category')
        if category_id:
            queryset = queryset.filter(category_id=category_id)

        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) | Q(description__icontains=search)
            )

        return queryset


class SignDetail(generics.RetrieveUpdateDestroyAPIView):
    """Детали, обновление и удаление знака"""
    queryset = Sign.objects.all()
    serializer_class = SignSerializer

    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]
        return [IsAuthenticated()]


# ========== ТЕСТЫ/ВИКТОРИНЫ ==========
class QuizList(generics.ListCreateAPIView):
    """Список тестов и создание нового"""
    queryset = Quiz.objects.prefetch_related('signs').all()
    serializer_class = QuizSerializer

    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAuthenticated()]
        return [AllowAny()]


class QuizDetail(generics.RetrieveUpdateDestroyAPIView):
    """Детали теста"""
    queryset = Quiz.objects.all()
    serializer_class = QuizSerializer


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def submit_quiz_result(request, quiz_id):
    """Отправка результата прохождения теста"""
    try:
        quiz = Quiz.objects.get(id=quiz_id)
        score = request.data.get('score', 0)
        total_questions = request.data.get('total_questions', 0)

        result = QuizResult.objects.create(
            user=request.user,
            quiz=quiz,
            score=score,
            total_questions=total_questions
        )

        serializer = QuizResultSerializer(result)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    except Quiz.DoesNotExist:
        return Response(
            {'error': 'Тест не найден'},
            status=status.HTTP_404_NOT_FOUND
        )


class UserQuizResults(generics.ListAPIView):
    """Результаты тестов текущего пользователя"""
    serializer_class = QuizResultSerializer

    def get_queryset(self):
        return QuizResult.objects.filter(user=self.request.user).select_related('quiz')


# ========== СТАТИСТИКА ==========
@api_view(['GET'])
def statistics(request):
    """Общая статистика системы"""
    stats = {
        'total_signs': Sign.objects.count(),
        'total_categories': Category.objects.count(),
        'total_quizzes': Quiz.objects.count(),
        'total_users': User.objects.count(),
        'total_quiz_results': QuizResult.objects.count(),
        'signs_by_type': dict(Sign.objects.values_list('sign_type').annotate(count=Count('id'))),
        'top_users': User.objects.annotate(
            quizzes_completed=Count('quiz_results')
        ).order_by('-quizzes_completed')[:5].values('username', 'quizzes_completed')
    }
    return Response(stats)


# ========== КОНСТРУКТОР ЗНАЧКОВ ==========
class BadgeProjectListCreate(generics.ListCreateAPIView):
    """Список проектов пользователя и создание нового"""
    serializer_class = BadgeProjectSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return BadgeProject.objects.filter(user=self.request.user)

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return BadgeProjectCreateSerializer
        return BadgeProjectSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class BadgeProjectDetail(generics.RetrieveUpdateDestroyAPIView):
    """Детали, обновление и удаление проекта"""
    serializer_class = BadgeProjectSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return BadgeProject.objects.filter(user=self.request.user)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def generate_badge_pdf(request, project_id):
    """Генерация PDF для печати значков"""
    from reportlab.lib.utils import ImageReader
    from PIL import Image
    import base64
    from io import BytesIO
    import math

    try:
        project = BadgeProject.objects.get(id=project_id, user=request.user)

        if project.orientation == 'landscape':
            pagesize = landscape(A4)
        else:
            pagesize = A4

        buffer = BytesIO()
        c = canvas.Canvas(buffer, pagesize=pagesize)
        width, height = pagesize

        mm = 2.83465
        margin = 15 * mm
        d = project.diameter_mm * mm

        cols = int((width - 2 * margin) // d)
        rows = int((height - 2 * margin) // d)

        start_x = (width - cols * d) / 2
        start_y = (height - rows * d) / 2

        for i in range(rows):
            for j in range(cols):
                idx = i * cols + j
                x = start_x + j * d
                y = start_y + i * d

                c.saveState()
                c.setStrokeColorRGB(0, 0, 0)
                c.setLineWidth(1)

                if project.shape_type == 'circle':
                    c.circle(x + d / 2, y + d / 2, d / 2)
                elif project.shape_type == 'square':
                    c.rect(x, y, d, d)
                elif project.shape_type == 'star':
                    center_x = x + d / 2
                    center_y = y + d / 2
                    points = []
                    outer_r = d / 2
                    inner_r = d / 4
                    for k in range(10):
                        angle = k * 36 * math.pi / 180
                        r = outer_r if k % 2 == 0 else inner_r
                        points.append(center_x + r * math.cos(angle))
                        points.append(center_y + r * math.sin(angle))
                    c.polygon(points)
                elif project.shape_type == 'shield':
                    c.polygon([
                        x + d / 2, y,
                        x + d, y + d / 3,
                        x + d, y + 2 * d / 3,
                        x + d / 2, y + d,
                        x, y + 2 * d / 3,
                        x, y + d / 3
                    ])
                elif project.shape_type == 'heart':
                    c.circle(x + d / 3, y + 2 * d / 3, d / 3)
                    c.circle(x + 2 * d / 3, y + 2 * d / 3, d / 3)
                    c.polygon([
                        x + d / 6, y + 2 * d / 3,
                        x + d / 2, y,
                        x + 5 * d / 6, y + 2 * d / 3
                    ])
                elif project.shape_type == 'oval':
                    c.ellipse(x, y + d / 4, x + d, y + 3 * d / 4)
                elif project.shape_type == 'hexagon':
                    center_x = x + d / 2
                    center_y = y + d / 2
                    points = []
                    for k in range(6):
                        angle = k * 60 * math.pi / 180
                        points.append(center_x + d / 2 * math.cos(angle))
                        points.append(center_y + d / 2 * math.sin(angle))
                    c.polygon(points)
                elif project.shape_type == 'cross':
                    c.rect(x + d / 3, y, d / 3, d)
                    c.rect(x, y + d / 3, d, d / 3)
                else:
                    c.rect(x, y, d, d)

                img_data = project.shapes_data.get(str(idx))
                if img_data and img_data != 'null' and not img_data.startswith('null'):
                    try:
                        if img_data.startswith('data:image'):
                            img_base64 = img_data.split(',')[1]
                        else:
                            img_base64 = img_data

                        img_bytes = base64.b64decode(img_base64)
                        img_buffer = BytesIO(img_bytes)

                        pil_img = Image.open(img_buffer)

                        if pil_img.mode in ('RGBA', 'LA', 'P'):
                            pil_img = pil_img.convert('RGB')

                        jpeg_buffer = BytesIO()
                        pil_img.save(jpeg_buffer, format='JPEG', quality=85)
                        jpeg_buffer.seek(0)

                        img_reader = ImageReader(jpeg_buffer)

                        padding = d * 0.1
                        c.drawImage(img_reader, x + padding, y + padding,
                                    d - 2 * padding, d - 2 * padding, mask='auto')
                    except Exception as e:
                        print(f"Ошибка загрузки изображения для индекса {idx}: {e}")

                c.restoreState()
                c.stroke()

        c.save()
        buffer.seek(0)

        response = HttpResponse(buffer.getvalue(), content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="badge_project_{project.id}.pdf"'
        return response

    except BadgeProject.DoesNotExist:
        return Response(
            {'error': 'Проект не найден'},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        print(f"Ошибка генерации PDF: {e}")
        return Response(
            {'error': f'Ошибка генерации PDF: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


# ========== ОБРАТНАЯ СВЯЗЬ ==========
class FeedbackCreateView(generics.CreateAPIView):
    """Публичный endpoint для отправки обратной связи. Не требует авторизации."""
    serializer_class = FeedbackCreateSerializer
    permission_classes = [AllowAny]

    def perform_create(self, serializer):
        user = self.request.user if self.request.user.is_authenticated else None

        x_forwarded_for = self.request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = self.request.META.get('REMOTE_ADDR')

        serializer.save(
            user=user,
            ip_address=ip,
            user_agent=self.request.META.get('HTTP_USER_AGENT', '')[:1000]
        )


class FeedbackListView(generics.ListAPIView):
    """Список обратной связи (только для staff)."""
    serializer_class = FeedbackSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if not self.request.user.is_staff:
            return Feedback.objects.none()
        return Feedback.objects.order_by('-created_at')


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def reply_to_feedback(request, feedback_id):
    """Ответ администратора на обратную связь"""
    if not request.user.is_staff:
        return Response(
            {'error': 'Доступ запрещён'},
            status=status.HTTP_403_FORBIDDEN
        )

    try:
        feedback = Feedback.objects.get(id=feedback_id)
    except Feedback.DoesNotExist:
        return Response(
            {'error': 'Сообщение не найдено'},
            status=status.HTTP_404_NOT_FOUND
        )

    response_text = request.data.get('response', '').strip()
    new_status = request.data.get('status', 'in_progress')

    if not response_text:
        return Response(
            {'error': 'Текст ответа обязателен'},
            status=status.HTTP_400_BAD_REQUEST
        )

    feedback.admin_response = response_text
    feedback.status = new_status
    feedback.responded_at = timezone.now()
    feedback.responded_by = request.user
    feedback.save()

    return Response(FeedbackSerializer(feedback).data)


# ========== АНАЛИТИКА (ДЛЯ АДМИНКИ) ==========
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def admin_dashboard_status(request):
    """Статистика для дашборда админки. Доступна только для staff."""
    if not request.user.is_staff:
        return Response(
            {'error': 'Доступ запрещён'},
            status=status.HTTP_403_FORBIDDEN
        )

    now = timezone.now()
    today = now.replace(hour=0, minute=0, second=0, microsecond=0)
    week_ago = now - timedelta(days=7)
    month_ago = now - timedelta(days=30)

    visits_today = SiteVisit.objects.filter(created_at__gte=today).count()
    visits_week = SiteVisit.objects.filter(created_at__gte=week_ago).count()
    visits_month = SiteVisit.objects.filter(created_at__gte=month_ago).count()
    visits_total = SiteVisit.objects.count()

    unique_today = SiteVisit.objects.filter(
        created_at__gte=today
    ).values('ip_address').distinct().count()

    unique_week = SiteVisit.objects.filter(
        created_at__gte=week_ago
    ).values('ip_address').distinct().count()

    users_total = User.objects.count()
    users_today = User.objects.filter(date_joined__gte=today).count()
    users_week = User.objects.filter(date_joined__gte=week_ago).count()

    feedback_new = Feedback.objects.filter(status='new').count()
    feedback_total = Feedback.objects.count()
    feedback_today = Feedback.objects.filter(created_at__gte=today).count()

    projects_total = BadgeProject.objects.count()
    projects_today = BadgeProject.objects.filter(created_at__gte=today).count()

    top_pages = list(
        SiteVisit.objects.filter(created_at__gte=week_ago)
        .values('path')
        .annotate(count=Count('id'))
        .order_by('-count')[:10]
    )

    top_browsers = list(
        SiteVisit.objects.filter(created_at__gte=week_ago)
        .exclude(browser='')
        .values('browser')
        .annotate(count=Count('id'))
        .order_by('-count')[:5]
    )

    top_os = list(
        SiteVisit.objects.filter(created_at__gte=week_ago)
        .exclude(os='')
        .values('os')
        .annotate(count=Count('id'))
        .order_by('-count')[:5]
    )

    mobile_count = SiteVisit.objects.filter(
        created_at__gte=week_ago, is_mobile=True
    ).count()

    desktop_count = SiteVisit.objects.filter(
        created_at__gte=week_ago, is_mobile=False
    ).count()

    visits_by_day = []
    for i in range(7):
        day_start = today - timedelta(days=6 - i)
        day_end = day_start + timedelta(days=1)
        count = SiteVisit.objects.filter(
            created_at__gte=day_start,
            created_at__lt=day_end
        ).count()
        visits_by_day.append({
            'date': day_start.strftime('%d.%m'),
            'count': count
        })

    recent_visits = SiteVisitSerializer(
        SiteVisit.objects.select_related('user').order_by('-created_at')[:20],
        many=True
    ).data

    recent_feedback = FeedbackSerializer(
        Feedback.objects.order_by('-created_at')[:10],
        many=True
    ).data

    return Response({
        'visits': {
            'today': visits_today,
            'week': visits_week,
            'month': visits_month,
            'total': visits_total,
            'unique_today': unique_today,
            'unique_week': unique_week,
        },
        'users': {
            'total': users_total,
            'today': users_today,
            'week': users_week,
        },
        'feedback': {
            'new': feedback_new,
            'total': feedback_total,
            'today': feedback_today,
        },
        'projects': {
            'total': projects_total,
            'today': projects_today,
        },
        'top_pages': top_pages,
        'top_browsers': top_browsers,
        'top_os': top_os,
        'devices': {
            'mobile': mobile_count,
            'desktop': desktop_count,
        },
        'visits_by_day': visits_by_day,
        'recent_visits': recent_visits,
        'recent_feedback': recent_feedback,
    })


class SiteVisitListView(generics.ListAPIView):
    """Список посещений (только для админов)"""
    serializer_class = SiteVisitSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if not self.request.user.is_staff:
            return SiteVisit.objects.none()
        return SiteVisit.objects.select_related('user').order_by('-created_at')