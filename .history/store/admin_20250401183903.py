from django.contrib import admin
from .models import Product, Color, Size

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'slug')
    search_fields = ('name', 'description', 'additional_info')
    prepopulated_fields = {"slug": ("name",)}

@admin.register(Color)
class ColorAdmin(admin.ModelAdmin):
    list_display = ('name', 'code')
    search_fields = ('name', 'code')

@admin.register(Size)
class SizeAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)