# accounts/forms.py
from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm

User = get_user_model()


# ────────────────────────────────────────────────────────────────
# 1.  Форма входа — русские лейблы + плейсхолдеры
# ────────────────────────────────────────────────────────────────
class CustomLoginForm(AuthenticationForm):
    username = forms.CharField(
        label="Логин",
        widget=forms.TextInput(attrs={
            "placeholder": "Ваш логин / e-mail / телефон",
            "autocomplete": "username",
        }),
    )
    password = forms.CharField(
        label="Пароль",
        strip=False,
        widget=forms.PasswordInput(attrs={
            "placeholder": "Пароль",
            "autocomplete": "current-password",
        }),
    )


# ────────────────────────────────────────────────────────────────
# 2.  Форма регистрации
# ────────────────────────────────────────────────────────────────
class SignUpForm(forms.ModelForm):
    """
    Регистрация:

      • username   – логин (обязателен)
      • first/last • e-mail • phone
      • пароль     – дважды (password1 / password2)
    """

    # поля, которых нет в модели
    username = forms.CharField(
        label="Логин",
        help_text="Латиница, цифры, «_». Будет использоваться для входа.",
        max_length=150,
        widget=forms.TextInput(attrs={
            "placeholder": "например, abuzada123",
            "autocomplete": "username",
        }),
    )
    password1 = forms.CharField(
        label="Пароль",
        widget=forms.PasswordInput(attrs={
            "placeholder": "Введите пароль",
            "autocomplete": "new-password",
        }),
    )
    password2 = forms.CharField(
        label="Повторите пароль",
        widget=forms.PasswordInput(attrs={
            "placeholder": "Ещё раз пароль",
            "autocomplete": "new-password",
        }),
    )

    # поля модели
    class Meta:
        model = User
        fields = ("username", "first_name", "last_name", "email", "phone")
        widgets = {
            "first_name": forms.TextInput(attrs={"placeholder": "Имя"}),
            "last_name":  forms.TextInput(attrs={"placeholder": "Фамилия"}),
            "email":      forms.EmailInput(attrs={"placeholder": "you@example.com"}),
            "phone":      forms.TextInput(attrs={"placeholder": "+7 999 123-45-67"}),
        }
        labels = {
            "first_name": "Имя",
            "last_name":  "Фамилия",
            "email":      "E-mail",
            "phone":      "Телефон",
        }

    # валидация совпадения паролей
    def clean(self):
        cleaned = super().clean()
        p1, p2 = cleaned.get("password1"), cleaned.get("password2")
        if p1 and p2 and p1 != p2:
            self.add_error("password2", "Пароли не совпадают")
        return cleaned

    # создание пользователя с хэшированием пароля
    def save(self, commit: bool = True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user