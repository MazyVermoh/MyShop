# store/models.py
from decimal import Decimal
import re

from django.conf     import settings
from django.core.validators import RegexValidator      #  ### новое
from django.db       import models
from django.utils    import timezone


# ───────────────────────────
# Справочники
# ───────────────────────────
class Size(models.Model):
    name = models.CharField(max_length=20, unique=True)

    def __str__(self):
        return self.name


class Color(models.Model):
    name = models.CharField(max_length=50, unique=True)
    code = models.CharField(max_length=7, blank=True, null=True)  # HEX

    def __str__(self):
        return self.name


# ───────────────────────────
# Товары
# ───────────────────────────
class Product(models.Model):
    name            = models.CharField(max_length=200)
    slug            = models.SlugField(unique=True)
    description     = models.TextField(blank=True, null=True)
    additional_info = models.TextField(blank=True, null=True)
    price           = models.DecimalField(max_digits=10, decimal_places=2)

    sizes  = models.ManyToManyField(Size,  related_name="products", blank=True)
    colors = models.ManyToManyField(Color, related_name="products", blank=True)

    def __str__(self):
        return self.name

    # главное фото / второе фото
    @property
    def main_photo(self):
        return self.images.first()

    @property
    def second_photo(self):
        main = self.main_photo
        return self.images.exclude(id=main.id).first() if main else None


class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE,
                                related_name="images")
    image   = models.ImageField(upload_to="products/")
    is_main = models.BooleanField(default=False)
    color   = models.ForeignKey(Color, on_delete=models.SET_NULL,
                                null=True, blank=True, related_name="images")

    class Meta:
        ordering = ["-is_main", "id"]

    def __str__(self):
        angle = "Front" if self.is_main else "Back"
        color_name = self.color.name if self.color else "no‑color"
        return f"{self.product.name} – {angle} – {color_name}"


# ───────────────────────────
# Заказы
# ───────────────────────────
phone_validator = RegexValidator(               #  ### новое
    regex=r"^\+?[0-9]{7,15}$",
    message="Введите корректный номер телефона (только цифры, 7‑15 символов)."
)

class Order(models.Model):
    STATUS_CHOICES = [
        ("new",       "Новый"),
        ("pending",   "Ожидает оплаты"),
        ("paid",      "Оплачен"),
        ("shipped",   "Отправлен"),
        ("finished",  "Завершён"),
        ("cancelled", "Отменён"),
    ]

    # варианты доставки
    SHIPPING_CHOICES = [                        #  ### обновлено
        ("courier", "Курьер (600 ₽)"),
        ("yandex",  "Пункт‑выдачи Яндекс"),
        ("cdek",    "Пункт‑выдачи СДЭК"),
    ]

    PAYMENT_CHOICES = [
        ("card",     "Банковской картой"),
        ("yoomoney", "YooMoney"),
        ("qiwi",     "QIWI"),
    ]

    # связь с пользователем (может быть аноним)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name="orders",
        verbose_name="Покупатель",
    )

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    status  = models.CharField(max_length=10, choices=STATUS_CHOICES, default="new")

    # контактные данные
    first_name = models.CharField(max_length=50)
    last_name  = models.CharField(max_length=50, blank=True)
    email      = models.EmailField()
    phone      = models.CharField(
        max_length=17, blank=True, validators=[phone_validator]
    )
    telegram   = models.CharField(              #  ### новое поле
        "Telegram", max_length=64, blank=True,
        help_text="username без @"
    )

    # адрес
    country  = models.CharField(max_length=40, default="RU")
    city     = models.CharField(max_length=40)
    address  = models.CharField("Улица, дом, кв.", max_length=255)
    postcode = models.CharField("Индекс", max_length=15, blank=True)

    # промокод
    promo_code = models.CharField(max_length=30, blank=True)
    discount   = models.DecimalField(max_digits=8, decimal_places=2,
                                     default=Decimal("0.00"))

    # доставка и оплата
    shipping_method = models.CharField(
        "Способ доставки", max_length=20,
        choices=SHIPPING_CHOICES, default="courier",
    )
    shipping_price  = models.DecimalField(      #  ### новое (курьер — 600 ₽)
        max_digits=8, decimal_places=2, default=Decimal("0.00")
    )
    payment_method  = models.CharField(
        "Способ оплаты", max_length=20,
        choices=PAYMENT_CHOICES, default="card",
    )

    def __str__(self):
        return f"Order #{self.id}"

    # итог с учётом скидки и доставки
    def total(self) -> Decimal:
        items_total = sum(item.total() for item in self.items.all())
        return items_total + self.shipping_price - self.discount


class OrderItem(models.Model):
    order    = models.ForeignKey(Order,   related_name="items",
                                 on_delete=models.CASCADE)
    product  = models.ForeignKey(Product, related_name="order_items",
                                 on_delete=models.PROTECT)
    price    = models.DecimalField(max_digits=8, decimal_places=2)
    qty      = models.PositiveIntegerField()
    size     = models.CharField(max_length=5, blank=True)
    color_id = models.PositiveIntegerField(null=True, blank=True)

    def total(self) -> Decimal:
        return self.price * self.qty


# ───────────────────────────
# Промокоды
# ───────────────────────────
class PromoCode(models.Model):
    PERCENT = "percent"
    FIXED   = "fixed"
    TYPE_CHOICES = [
        (PERCENT, "Процентная скидка"),
        (FIXED,   "Фиксированная сумма"),
    ]

    code     = models.CharField(max_length=30, unique=True)
    discount = models.DecimalField(
        max_digits=5, decimal_places=2,
        help_text="Если процентная — 0‑100, иначе сумма в рублях."
    )
    type       = models.CharField(max_length=10, choices=TYPE_CHOICES, default=PERCENT)
    active     = models.BooleanField(default=True)
    valid_from = models.DateTimeField(default=timezone.now)
    valid_to   = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.code

    # проверка валидности
    def is_valid(self):
        now = timezone.now()
        return (self.active
                and self.valid_from <= now
                and (self.valid_to is None or now <= self.valid_to))

    # расчёт скидки
    def calculate_discount(self, total_amount: Decimal) -> Decimal:
        if not self.is_valid():
            return Decimal("0")
        if self.type == self.PERCENT:
            return (total_amount * self.discount / Decimal("100")).quantize(
                Decimal("0.01")
            )
        return min(self.discount, total_amount)