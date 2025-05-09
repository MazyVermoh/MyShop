# checkout/utils.py

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.urls import reverse

def send_order_confirmation(order):
    """
    Письмо клиенту: 
    тема, текст и HTML-версия берутся из шаблонов,
    отправляем на order.email.
    """
    # 1) тема
    subject = f"Ваш заказ #{order.id} на ABUZADA STORE принят"
    from_email = settings.DEFAULT_FROM_EMAIL
    to = [order.email]

    # 2) рендерим текстовые шаблоны
    text_body = render_to_string("checkout/email/order_confirmation.txt", {
        "order": order,
        "site_url": settings.SITE_URL,  # не забудьте добавить в settings
        "status_url": settings.SITE_URL + reverse("checkout:order_status", args=[order.id]),
    })
    html_body = render_to_string("checkout/email/order_confirmation.html", {
        "order": order,
        "site_url": settings.SITE_URL,
        "status_url": settings.SITE_URL + reverse("checkout:order_status", args=[order.id]),
    })

    # 3) отправляем multipart-письмо
    msg = EmailMultiAlternatives(subject, text_body, from_email, to)
    msg.attach_alternative(html_body, "text/html")
    msg.send()


def notify_admin_new_order(order):
    """
    Письмо админу(ам) о новом заказе.
    Берёт список адресов из settings.ADMINS (или settings.MANAGERS).
    """
    subject = f"[ADMIN] Новый заказ #{order.id}"
    from_email = settings.DEFAULT_FROM_EMAIL
    # здесь ADMINS — список кортежей (имя, email)
    to = [email for _, email in settings.ADMINS]

    body = render_to_string("checkout/email/admin_notification.txt", {
        "order": order,
        "site_url": settings.SITE_URL,
    })

    # простое текстовое письмо
    EmailMultiAlternatives(subject, body, from_email, to).send()