from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from . import views

urlpatterns = [
    # ========== АВТОРИЗАЦИЯ ==========
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('register/', views.RegisterView.as_view(), name='register'),
    
    # ========== ПОЛЬЗОВАТЕЛИ ==========
    path('users/', views.UserList.as_view(), name='user-list'),
    path('users/<int:pk>/', views.UserDetail.as_view(), name='user-detail'),
    path('profile/', views.user_profile, name='user-profile'),
    
    # ========== КАТЕГОРИИ ==========
    path('categories/', views.CategoryList.as_view(), name='category-list'),
    path('categories/<int:pk>/', views.CategoryDetail.as_view(), name='category-detail'),
    
    # ========== ЗНАКИ ==========
    path('signs/', views.SignList.as_view(), name='sign-list'),
    path('signs/<int:pk>/', views.SignDetail.as_view(), name='sign-detail'),
    
    # ========== ТЕСТЫ ==========
    path('quizzes/', views.QuizList.as_view(), name='quiz-list'),
    path('quizzes/<int:pk>/', views.QuizDetail.as_view(), name='quiz-detail'),
    path('quizzes/<int:quiz_id>/submit/', views.submit_quiz_result, name='submit-quiz-result'),
    path('my-quiz-results/', views.UserQuizResults.as_view(), name='my-quiz-results'),
    
    # ========== СТАТИСТИКА ==========
    path('statistics/', views.statistics, name='statistics'),
    
    # ========== КОНСТРУКТОР ЗНАЧКОВ ==========
    path('badge-projects/', views.BadgeProjectListCreate.as_view(), name='badge-project-list'),
    path('badge-projects/<int:pk>/', views.BadgeProjectDetail.as_view(), name='badge-project-detail'),
    path('badge-projects/<int:project_id>/generate-pdf/', views.generate_badge_pdf, name='generate-badge-pdf'),
]