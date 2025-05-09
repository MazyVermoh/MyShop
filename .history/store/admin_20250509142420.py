from django.contrib import admin
from .models import Size, Color, Product, ProductImage, Order, OrderItem, PromoCode, Subscriber
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings

@admin.register(Size)
class SizeAdmin(admin.ModelAdmin):
    list_display = ("name",)


@admin.register(Color)
class ColorAdmin(admin.ModelAdmin):
    list_display = ("name", "code")


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "price")
    prepopulated_fields = {"slug": ("name",)}
    inlines = [ProductImageInline]


@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ("image_label", "color", "is_main")
    list_filter = ("product", "color", "is_main")
    search_fields = ("product__name",)

    def image_label(self, obj):
        """
        Показываем в списке:
         - имя товара,
         - 'Front' если is_main=True, иначе 'Back',
         - имя цвета (или 'no-color')
        """
        angle = "Front" if obj.is_main else "Back"
        color_name = obj.color.name if obj.color else "no-color"
        return f"{obj.product.name} – {angle} – {color_name}"

    image_label.short_description = "Image"

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        "id", "created", "status",
        "first_name", "email",
        "shipping_method", "payment_method",
        "total_display",
        "user",
    )
    autocomplete_fields = ("user",)
    # … при необходимости добавьте search_fields, list_filter …

    def total_display(self, obj):
        return f"{obj.total():.2f} ₽"
    total_display.short_description = "Итог"
    
@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'product', 'qty', 'price')

@admin.register(PromoCode)
class PromoCodeAdmin(admin.ModelAdmin):
    list_display = ('code', 'type', 'discount', 'active', 'valid_from', 'valid_to')
    list_filter  = ('type', 'active')
    search_fields = ('code',)
    
@admin.register(Subscriber)
class SubscriberAdmin(admin.ModelAdmin):
    list_display = ("email", "created_at", "confirmed")
    list_filter = ("confirmed", "created_at")
    search_fields = ("email",)
    actions = ["send_newsletter"]

    def send_newsletter(self, request, queryset):
        """
        Action: отсылает письмо всем отмеченным подписчикам с confirmed=True.
        """
        subs = queryset.filter(confirmed=True)
        recipients = list(subs.values_list("email", flat=True))
        if not recipients:
            self.message_user(request, "Нет подтверждённых подписчиков.", level=admin.WARNING)
            return

        # Тема и содержимое письма
        subject = "MyShop — Новые поступления и акции!"
        html_message = render_to_string("emails/newsletter.html", {
            # сюда можно передать любые переменные для шаблона
            "items": [],  
        })

        send_mail(
            subject=subject,
            message="",  # текстовая часть, если нужна
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=recipients,
            html_message=html_message,
            fail_silently=False,
        )
        self.message_user(request, f"Письмо отправлено {len(recipients)} подписчикам.")

    send_newsletter.short_description = "Отправить письмо выбранным подписчикам"