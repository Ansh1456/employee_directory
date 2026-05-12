from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import redirect

urlpatterns = [
    path('', lambda request: redirect('dashboard'), name='root'),
    path('admin/', admin.site.urls),
    path('', include('users.urls')),
    path('', include('employees.urls')),
    path('', include('departments.urls')),
    path('api/v1/', include('api.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
