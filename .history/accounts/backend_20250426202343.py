from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend

User = get_user_model()

class EmailPhoneUsernameBackend(ModelBackend):
    """
    Принимает username ИЛИ e-mail ИЛИ phone в поле `username` формы логина.
    """
    def authenticate(self, request, username=None, password=None, **kwargs):
        if username is None or password is None:
            return None
        qs = User.objects.filter(
            models.Q(username__iexact=username) |
            models.Q(email__iexact=username)    |
            models.Q(phone__iexact=username)
        )
        try:
            user = qs.get()
        except User.DoesNotExist:
            return None
        if user.check_password(password) and self.user_can_authenticate(user):
            return user