# accounts/forms.py
from django import forms
from django.contrib.auth import get_user_model

User = get_user_model()


class SignUpForm(forms.ModelForm):
    """
    Форма регистрации:

    • username — видимый логин (обязательно)
    • first_name / last_name / e-mail / phone
    • пароль вводится дважды (password1 / password2)

    После валидации создаём пользователя и хэшируем пароль.
    """

    # ───────── дополнительные поля, которых нет в модели ──────────
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
            "autocomplete": "new-password",
            "placeholder": "Введите пароль",
        }),
    )
    password2 = forms.CharField(
        label="Повторите пароль*",
        widget=forms.PasswordInput(attrs={
            "autocomplete": "new-password",
            "placeholder": "Ещё раз пароль",
        }),
    )

    # ───────── поля, которые лежат в самой модели ──────────
    class Meta:
        model  = User
        fields = (
            "username",
            "first_name",
            "last_name",
            "email",
            "phone",
        )
        widgets = {
            "first_name": forms.TextInput(attrs={"placeholder": "Имя"}),
            "last_name":  forms.TextInput(attrs={"placeholder": "Фамилия"}),
            "email":      forms.EmailInput(attrs={"placeholder": "you@example.com"}),
            "phone":      forms.TextInput(attrs={"placeholder": "+7 999 123-45-67"}),
        }
        labels = {
            "first_name": "Имя",
            "last_name":  "Фамилия",
            "email":      "E-mail",
            "phone":      "Телефон",
        }

    # ───────── валидация паролей ──────────
    def clean(self):
        cleaned = super().clean()
        p1 = cleaned.get("password1")
        p2 = cleaned.get("password2")
        if p1 and p2 and p1 != p2:
            self.add_error("password2", "Пароли не совпадают")
        return cleaned

    # ───────── сохранение пользователя ──────────
    def save(self, commit: bool = True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user