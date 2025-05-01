from django.db import models

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
        """
        Первое изображение: по Meta.ordering сначала идёт is_main=True, затем по id.
        """
        return self.images.first()

    @property
    def second_photo(self):
        """
        Любое изображение, отличное от main_photo.
        """
        main = self.main_photo
        return self.images.exclude(id=main.id).first() if main else None


class ProductImage(models.Model):
    product  = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="images"
    )
    image    = models.ImageField(upload_to="products/")
    is_main  = models.BooleanField(default=False)
    color    = models.ForeignKey(
        Color, related_name="images",
        null=True, blank=True, on_delete=models.SET_NULL
    )

    class Meta:
        # Сначала помеченные как is_main=True, потом по возрастанию id
        ordering = ["-is_main", "id"]

    def __str__(self):
        # При желании можно добавить angle/front‑back в строковое представление
        return f"{self.product.name} – {'Main' if self.is_main else 'Other'} – {self.color or 'no‑color'}"