from django.db import models
from decimal import Decimal
from django.conf import settings
from django.utils import timezone


class Size(models.Model):
    name = models.CharField(max_length=20, unique=True)

    def __str__(self):
        return self.name


class Color(models.Model):
    name = models.CharField(max_length=50, unique=True)
    code = models.CharField(max_length=7, blank=True, null=True)  # HEX

    def __str__(self):
        return self.name


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

    @property
    def main_photo(self):
        # главное изображение — первое в порядке Meta.ordering
        return self.images.first()

    @property
    def second_photo(self):
        # любое отличное от main_photo
        main = self.main_photo
        return self.images.exclude(id=main.id).first() if main else None


class ProductImage(models.Model):
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="images"
    )
    image   = models.ImageField(upload_to="products/")
    is_main = models.BooleanField(default=False)
    color   = models.ForeignKey(
        Color, on_delete=models.SET_NULL, null=True, blank=True, related_name="images"
    )

    class Meta:
        # Сначала помеченные как main, потом по возрастанию id
        ordering = ["-is_main", "id"]

    def __str__(self):
        # Выведем: "<Product> – Front/Back – <Color>"
        angle = "Front" if self.is_main else "Back"
        color_name = self.color.name if self.color else "no-color"
        return f"{self.product.name} – {angle} – {color_name}"

class Order(models.Model):
    STATUS_CHOICES = [
        ("new",       "Новый"),
        ("pending",   "Ожидает оплаты"),
        ("paid",      "Оплачен"),
        ("shipped",   "Отправлен"),
        ("finished",  "Завершён"),
        ("cancelled", "Отменён"),
    ]

    created      = models.DateTimeField(auto_now_add=True)
    updated      = models.DateTimeField(auto_now=True)
    status       = models.CharField(max_length=10, choices=STATUS_CHOICES, default="new")

    # контакт + доставка
    first_name   = models.CharField(max_length=50)
    last_name    = models.CharField(max_length=50)
    email        = models.EmailField()
    phone        = models.CharField(max_length=20, blank=True)

    country      = models.CharField(max_length=40)
    city         = models.CharField(max_length=40)
    address      = models.CharField(max_length=255)
    postcode     = models.CharField(max_length=15, blank=True)

    promo_code   = models.CharField(max_length=30, blank=True)
    discount     = models.DecimalField(max_digits=8, decimal_places=2, default=0)  # ₽

    def __str__(self):
        return f"Order #{self.id}"

    def total(self) -> Decimal:
        items_total = sum(i.total() for i in self.items.all())
        return items_total - self.discount


class OrderItem(models.Model):
    order     = models.ForeignKey(Order, related_name="items", on_delete=models.CASCADE)
    product   = models.ForeignKey("store.Product", on_delete=models.PROTECT)
    price     = models.DecimalField(max_digits=8, decimal_places=2)
    qty       = models.PositiveIntegerField()
    size      = models.CharField(max_length=5, blank=True)
    color_id  = models.PositiveIntegerField(null=True, blank=True)

    def total(self):
        return self.price * self.qty

class PromoCode(models.Model):
    PERCENT = 'percent'
    FIXED   = 'fixed'
    TYPE_CHOICES = [
        (PERCENT, 'Процентная скидка'),
        (FIXED,   'Фиксированная сумма'),
    ]

    code        = models.CharField(max_length=30, unique=True)
    discount    = models.DecimalField(
        max_digits=5, decimal_places=2,
        help_text='Если процентная — в диапазоне 0–100, иначе в валюте.'
    )
    type        = models.CharField(
        max_length=10, choices=TYPE_CHOICES, default=PERCENT
    )
    active      = models.BooleanField(default=True)
    valid_from  = models.DateTimeField(default=timezone.now)
    valid_to    = models.DateTimeField(null=True, blank=True,
                                       help_text='До какого момента действует.')

    def is_valid(self):
        now = timezone.now()
        return (self.active
                and self.valid_from <= now
                and (self.valid_to is None or now <= self.valid_to))

    def calculate_discount(self, total_amount):
        """
        Возвращает сумму скидки в той же валюте, что total_amount.
        """
        if not self.is_valid():
            return Decimal('0')
        if self.type == PromoCode.PERCENT:
            return (total_amount * self.discount / Decimal('100')).quantize(
                Decimal('0.01')
            )
        else:
            return min(self.discount, total_amount)

    def __str__(self):
        return self.code