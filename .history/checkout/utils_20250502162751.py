# checkout/utils.py

from django.conf import settings
from django.core.mail import EmailMultiAlternatives, mail_admins
from django.template.loader import render_to_string

def send_order_confirmation(order):
    """
    Письмо клиенту сразу после создания заказа.
    """
    ctx = {
        "order": order,
        "site_url": getattr(settings, "SITE_URL", ""),  # можно добавить SITE_URL в settings
    }
    subject = f"Ваш заказ #{order.id} принят"
    text_body = render_to_string("emails/order_confirmation.txt", ctx)
    html_body = render_to_string("emails/order_confirmation.html", ctx)

    msg = EmailMultiAlternatives(
        subject=subject,
        body=text_body,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[order.email],
    )
    msg.attach_alternative(html_body, "text/html")
    msg.send()

def notify_admin_new_order(order):
    """
    Уведомление администраторам о новом заказе.
    """
    ctx = {
        "order": order,
        "site_url": getattr(settings, "SITE_URL", ""),
    }
    subject = f"Новый заказ #{order.id}"
    text_body = render_to_string("emails/new_order_notification.txt", ctx)
    html_body = render_to_string("emails/new_order_notification.html", ctx)

    # mail_admins использует список ADMINS из settings
    mail_admins(subject, text_body, html_message=html_body)