from django.contrib import admin
from django.urls import path, include
# добавляем
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('store.urls')),  # Ваши маршруты приложения store
]

# ------------------------------
#   Подключаем раздачу MEDIA файлов в режиме DEBUG
# ------------------------------
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)