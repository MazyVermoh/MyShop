import os
import sys

# 1) Указываем путь к корню проекта (там, где manage.py)
project_root = os.path.dirname(__file__)
sys.path.insert(0, project_root)

# 2) Устанавливаем переменную окружения для Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "myshop.settings")

# 3) Запускаем WSGI-приложение
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()