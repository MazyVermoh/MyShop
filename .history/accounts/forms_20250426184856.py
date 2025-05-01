# accounts/forms.py
from django import forms
from django.contrib.auth.forms import (
    AuthenticationForm,
    UserCreationForm,
)
from django.contrib.auth import get_user_model

User = get_user_model()


class SignUpForm(UserCreationForm):
    """
    Регистрация: имя, фамилия, e-mail *или* телефон (одного поля достаточно),
    плюс пароль ×2.
    """
    first_name = forms.CharField(
        label="Имя",
        max_length=30,
        widget=forms.TextInput(attrs={"placeholder": "Имя"}),
    )
    last_name = forms.CharField(
        label="Фамилия",
        max_length=30,
        widget=forms.TextInput(attrs={"placeholder": "Фамилия"}),
        required=False,
    )
    email = forms.EmailField(
        label="E-mail",
        required=False,
        widget=forms.EmailInput(attrs={"placeholder": "E-mail"}),
    )
    phone = forms.CharField(
        label="Телефон",
        required=False,
        widget=forms.TextInput(attrs={"placeholder": "+7…"}),
        help_text="Можно указать либо телефон, либо e-mail",
    )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("first_name", "last_name", "email", "phone")

    # ─────────────────────────────────────────────────────────────
    #  Валидация: нужен хотя бы один контакт (e-mail или телефон)
    # ─────────────────────────────────────────────────────────────
    def clean(self):
        cleaned = super().clean()
        email = cleaned.get("email")
        phone = cleaned.get("phone")
        if not email and not phone:
            raise forms.ValidationError(
                "Укажите хотя бы e-mail или номер телефона."
            )
        return cleaned


class SignInForm(AuthenticationForm):
    """
    Авторизация по логину (e-mail или телефон) и паролю.
    """
    username = forms.CharField(
        label="E-mail или телефон",
        widget=forms.TextInput(attrs={"placeholder": "E-mail или телефон"}),
    )
    password = forms.CharField(
        label="Пароль",
        strip=False,
        widget=forms.PasswordInput(attrs={"placeholder": "Пароль"}),
    )