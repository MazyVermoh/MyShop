# accounts/models.py
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.crypto import get_random_string
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    """
    Кастомный пользователь:
      • email и phone уникальны
      • username скрыт от форм и генерируется автоматически
    """
    email = models.EmailField(_("e-mail"), unique=True)
    phone = models.CharField(_("телефон"), max_length=20, unique=True)

    # first_name, last_name, password — уже есть в AbstractUser
    REQUIRED_FIELDS = ["email", "phone", "first_name", "last_name"]
    USERNAME_FIELD = "username"   # пока оставляем username «техническим»

    def save(self, *args, **kwargs):
        # если username пуст — создаём что-то вроде "user_A8X1zB4Q"
        if not self.username:
            self.username = f"user_{get_random_string(8)}"
        super().save(*args, **kwargs)

    def __str__(self):
        full = self.get_full_name()
        return full or self.email or self.username