# accounts/backends.py
"""
Кастомный backend даёт возможность авторизоваться
  • по username
  • по e-mail
  • по телефону
в одном и том же поле формы «Username».
"""

from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend
from django.db import models

User = get_user_model()


class EmailPhoneUsernameBackend(ModelBackend):
    """
    Проверяем пароль так же, как стандартный ModelBackend,
    но пользователя ищем по username ИЛИ e-mail ИЛИ phone.
    """

    def authenticate(self, request, username=None, password=None, **kwargs):
        if not username or not password:
            return None

        # пытаемся найти одного пользователя с совпадением
        try:
            user = User.objects.get(
                models.Q(username__iexact=username) |
                models.Q(email__iexact=username) |
                models.Q(phone__iexact=username)
            )
        except User.DoesNotExist:
            return None
        except User.MultipleObjectsReturned:
            return None   # дубликаты — лучше не пускать

        # проверяем пароль
        if user.check_password(password) and self.user_can_authenticate(user):
            return user
        return None