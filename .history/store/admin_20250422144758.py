from django.contrib import admin
from .models import Product, ProductImage, Size, Color


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display  = ("name", "slug", "price")
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ("name", "description", "additional_info")
    filter_horizontal = ("sizes", "colors")            # удобный выбор


@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ("product", "color", "is_main")
    list_filter  = ("product", "color")
    search_fields = ("product__name",)


@admin.register(Size)
class SizeAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)


@admin.register(Color)
class ColorAdmin(admin.ModelAdmin):
    list_display = ("name", "code")
    search_fields = ("name",)