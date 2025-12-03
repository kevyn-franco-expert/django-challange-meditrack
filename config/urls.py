from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('apps.patients.urls')),
    path('api/', include('apps.records.urls')),
]