from django.db import models

class Color(models.Model):
    """
    Модель для хранения информации о цветах (white, cream, black).
    """
    name = models.CharField(max_length=50)
    code = models.CharField(max_length=7, blank=True, null=True)

    def __str__(self):
        return self.name

class Size(models.Model):
    """
    Модель для хранения информации о доступных размерах (S, M, L, XL и т.д.).
    """
    name = models.CharField(max_length=5)

    def __str__(self):
        return self.name

class Product(models.Model):
    """
    Основная модель товара (футболки и т.п.).
    """
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True, null=True)
    additional_info = models.TextField(blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    # Многие-ко-многим для цветов и размеров (если нужно)
    # Если не используете, можно убрать эти поля
    # colors = models.ManyToManyField(Color, blank=True)
    # sizes = models.ManyToManyField(Size, blank=True)

    def __str__(self):
        return self.name

class ProductImage(models.Model):
    """
    Модель для хранения нескольких фотографий, связанных с товаром.
    """
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="images"
    )
    image = models.ImageField(upload_to="products/")
    is_main = models.BooleanField(default=False)

    def __str__(self):
        return f"Image for {self.product.name} (ID: {self.id})"