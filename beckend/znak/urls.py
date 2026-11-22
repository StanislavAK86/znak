from django.contrib import admin
from django.urls import path, include
from znakapp.admin_dashboard import dashboard_view

urlpatterns = [
    path('admin/dashboard/', dashboard_view, name='admin-dashboard'),
    path('admin/', admin.site.urls),
    path('api/', include('znakapp.urls')),
]