from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.static import serve
import os

def serve_frontend(request):
    """Servir el archivo HTML sin procesarlo como template"""
    file_path = os.path.join(settings.BASE_DIR, 'frontend', 'index.html')
    return serve(request, 'index.html', document_root=os.path.join(settings.BASE_DIR, 'frontend'))

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/', include('accounts.urls')),
    path('api/', include('predictions.urls')),
    path('', serve_frontend, name='home'),  # Cambiar esta línea
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)