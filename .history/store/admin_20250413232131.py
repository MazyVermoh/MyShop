from django.contrib import admin
from .models import Product, ProductImage, Size, Color

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'price')
    search_fields = ('name', 'description', 'additional_info')
    prepopulated_fields = {"slug": ("name",)}
    filter_horizontal = ('sizes', 'colors')  # Удобный выбор размеров в админке

@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ('product', 'image', 'is_main')
    search_fields = ('product__name',)

@admin.register(Size)
class SizeAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

@admin.register(Color)
class ColorAdmin(admin.ModelAdmin):
    list_display = ('name', 'code')
    search_fields = ('name',)