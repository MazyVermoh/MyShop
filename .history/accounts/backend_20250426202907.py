# accounts/backends.py
"""
Логин по username, e-mail или телефону в одном поле.
"""

from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend
from django.db import models

User = get_user_model()


class EmailPhoneUsernameBackend(ModelBackend):
    """authenticate(username=..., password=...)"""
    def authenticate(self, request, username=None, password=None, **kwargs):
        if not username or not password:
            return None

        try:
            user = User.objects.get(
                models.Q(username__iexact=username) |
                models.Q(email__iexact=username) |
                models.Q(phone__iexact=username)
            )
        except (User.DoesNotExist, User.MultipleObjectsReturned):
            return None

        if user.check_password(password) and self.user_can_authenticate(user):
            return user
        return None