from django.db import models
from decimal import Decimal
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
        return self.images.first()

    @property
    def second_photo(self):
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
        ordering = ["-is_main", "id"]

    def __str__(self):
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

    SHIPPING_CHOICES = [
        ("courier", "Курьер"),
        ("pickup",  "Самовывоз"),
    ]
    PAYMENT_CHOICES = [
        ("card",     "Банковской картой"),
        ("yoomoney", "YooMoney"),
        ("qiwi",     "QIWI"),
    ]

    created         = models.DateTimeField(auto_now_add=True)
    updated         = models.DateTimeField(auto_now=True)
    status          = models.CharField(max_length=10, choices=STATUS_CHOICES, default="new")

    # контакт + доставка
    first_name      = models.CharField(max_length=50)
    last_name       = models.CharField(max_length=50)
    email           = models.EmailField()
    phone           = models.CharField(max_length=20, blank=True)

    country         = models.CharField(max_length=40)
    city            = models.CharField(max_length=40)
    address         = models.CharField(max_length=255)
    postcode        = models.CharField(max_length=15, blank=True)

    # промокод
    promo_code      = models.CharField(max_length=30, blank=True)
    discount        = models.DecimalField(max_digits=8, decimal_places=2, default=Decimal('0.00'))

    shipping_method = models.CharField(
        "Способ доставки", max_length=20,
        choices=SHIPPING_CHOICES, default="courier",
    )
    payment_method  = models.CharField(
        "Способ оплаты", max_length=20,
        choices=PAYMENT_CHOICES, default="card",
    )

    def __str__(self):
        return f"Order #{self.id}"

    def total(self) -> Decimal:
        items_total = sum(i.total() for i in self.items.all())
        return items_total - self.discount


class OrderItem(models.Model):
    order     = models.ForeignKey(Order, related_name="items", on_delete=models.CASCADE)
    product   = models.ForeignKey(Product, on_delete=models.PROTECT, related_name="order_items")
    price     = models.DecimalField(max_digits=8, decimal_places=2)
    qty       = models.PositiveIntegerField()
    size      = models.CharField(max_length=5, blank=True)
    color_id  = models.PositiveIntegerField(null=True, blank=True)

    def total(self) -> Decimal:
        return self.price * self.qty


