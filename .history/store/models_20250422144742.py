from django.db import models


class Size(models.Model):
    name = models.CharField(max_length=20, unique=True)

    def __str__(self):
        return self.name


class Color(models.Model):
    name = models.CharField(max_length=50, unique=True)
    code = models.CharField(max_length=7, blank=True, null=True)          # HEX

    def __str__(self):
        return self.name


class Product(models.Model):
    name            = models.CharField(max_length=200)
    slug            = models.SlugField(unique=True)
    description     = models.TextField(blank=True, null=True)
    additional_info = models.TextField(blank=True, null=True)
    price           = models.DecimalField(max_digits=10, decimal_places=2)

    sizes  = models.ManyToManyField(Size,   related_name="products", blank=True)
    colors = models.ManyToManyField(Color,  related_name="products", blank=True)

    def __str__(self):
        return self.name

    # главное и второе фото — как было
    @property
    def main_photo(self):
        return self.images.filter(is_main=True).first() or self.images.first()

    @property
    def second_photo(self):
        pics = list(self.images.all())
        return pics[1] if len(pics) > 1 else None


class ProductImage(models.Model):
    product  = models.ForeignKey(Product, on_delete=models.CASCADE,
                                 related_name="images")
    image    = models.ImageField(upload_to="products/")
    is_main  = models.BooleanField(default=False)

    # 🔥 НОВОЕ: к какому цвету относится фото
    color    = models.ForeignKey(Color, related_name="images",
                                 null=True, blank=True,
                                 on_delete=models.SET_NULL)

    def __str__(self):
        return f"{self.product.name} – {self.color or 'no‑color'} (id={self.id})"