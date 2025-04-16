from django.db import models

class Product(models.Model):
    """
    Основная модель товара (например, футболки и т.п.).
    Убраны связи с цветами и размерами.
    """
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True, null=True)
    additional_info = models.TextField(blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.name

    @property
    def main_photo(self):
        """
        Возвращает основное изображение товара (is_main=True), 
        если такого нет – возвращает None.
        """
        return self.images.filter(is_main=True).first()

    @property
    def second_photo(self):
        """
        Возвращает второе изображение из списка product.images.all(),
        если оно существует, иначе None.
        """
        images_list = list(self.images.all())
        if len(images_list) > 1:
            return images_list[1]
        return None

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