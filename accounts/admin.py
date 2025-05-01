from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth import get_user_model

User = get_user_model()

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    """Отображаем нашу кастом-модель в админке так же, как стандартный User."""
    list_display = ("email", "phone", "first_name", "last_name", "is_staff")
    search_fields = ("email", "phone", "first_name", "last_name")
    ordering = ("email",)

    # какие поля видны в форме add / change
    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("email", "phone", "password1", "password2"),
        }),
    )
    fieldsets = (
        (None, {"fields": ("email", "phone", "password")}),
        ("Personal info", {"fields": ("first_name", "last_name")}),
        ("Permissions",  {"fields": ("is_active", "is_staff", "is_superuser",
                                     "groups", "user_permissions")}),
        ("Important dates", {"fields": ("last_login",)}),
    )