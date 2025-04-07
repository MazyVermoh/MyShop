from django.db import models

class Color(models.Model):
    """
    Хранит информацию о каждом цвете.
    """
    name = models.CharField(max_length=50)
    # Опционально можно хранить код цвета (hex), 
    # чтобы при необходимости отображать закрашенный кружок в интерфейсе
    code = models.CharField(max_length=7, blank=True, null=True)

    def __str__(self):
        return self.name

class Size(models.Model):
    """
    Хранит информацию о доступных размерах (S, M, L, XL и т.д.).
    """
    name = models.CharField(max_length=5)

    def __str__(self):
        return self.name

class Product(models.Model):
    """
    Основная модель товара. Теперь у нас 
    есть ManyToMany-поля для цветов и размеров.
    """
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True, null=True)
    # Дополнительное поле для отдельной информации (если понадобится)
    additional_info = models.TextField(blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to='products/', blank=True, null=True)

    # Многие-ко-многим: один товар может иметь несколько цветов и размеров
    colors = models.ManyToManyField(Color, blank=True)
    sizes = models.ManyToManyField(Size, blank=True)

    def __str__(self):
        return self.name