from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('znakapp.urls')),  # Все API будут доступны по префиксу /api/
]