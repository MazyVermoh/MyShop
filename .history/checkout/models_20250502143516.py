# checkout/models.py

from django.db import models

class Order(models.Model):
    STATUS_CHOICES = [
        ("new",       "Новый"),
        ("pending",   "Ожидает оплаты"),
        ("paid",      "Оплачен"),
        ("shipped",   "Отправлен"),
        ("finished",  "Завершён"),
        ("cancelled", "Отменён"),
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

    # поля для промокода/скидки
    promo_code      = models.CharField(max_length=30, blank=True)
    discount        = models.DecimalField(max_digits=8, decimal_places=2, default=0)

    def __str__(self):
        return f"Order #{self.id}"

    def total(self):
        return sum(item.total() for item in self.items.all()) - self.discount


class OrderItem(models.Model):
    order     = models.ForeignKey(Order, related_name="items", on_delete=models.CASCADE)
    product   = models.ForeignKey("store.Product", on_delete=models.PROTECT)
    price     = models.DecimalField(max_digits=8, decimal_places=2)
    qty       = models.PositiveIntegerField()
    size      = models.CharField(max_length=5, blank=True)
    color_id  = models.PositiveIntegerField(null=True, blank=True)

    def total(self):
        return self.price * self.qty