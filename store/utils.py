# store/utils.py  (создайте, если нет)

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.urls import reverse

def send_subscribe_confirmation(subscriber):
    """
    Отправляет письмо с ссылкой вида
    http://site/subscribe/confirm/<token>/
    """
    subject = "Подтверждение подписки на новости ABUZADA STORE"
    from_email = settings.DEFAULT_FROM_EMAIL
    to = [subscriber.email]

    # генерируем токен (можно на hashlib + SECRET_KEY)
    import hashlib, time
    token_src = f"{subscriber.email}{settings.SECRET_KEY}{time.time()}"
    token = hashlib.sha256(token_src.encode()).hexdigest()

    # сохраним токен в сессии (или сделайте отдельную модель, если хотите)
    # для простоты — session
    subscriber_token_key = f"subscriber-{subscriber.id}-token"
    # при повторной отправке перезаписываем
    subscriber._token = token  # временно на объект, чтобы передать в шаблон

    confirm_url = f"{settings.SITE_URL}{reverse('store:subscribe_confirm', args=[subscriber.id, token])}"

    text_body = render_to_string("store/email/subscribe_confirm.txt", {
        "confirm_url": confirm_url,
    })
    html_body = render_to_string("store/email/subscribe_confirm.html", {
        "confirm_url": confirm_url,
    })

    msg = EmailMultiAlternatives(subject, text_body, from_email, to)
    msg.attach_alternative(html_body, "text/html")
    msg.send()