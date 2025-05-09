from django.contrib import admin
from .models import Size, Color, Product, ProductImage, Order, OrderItem, PromoCode

@admin.register(Size)
class SizeAdmin(admin.ModelAdmin):
    list_display = ("name",)


@admin.register(Color)
class ColorAdmin(admin.ModelAdmin):
    list_display = ("name", "code")


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "price")
    prepopulated_fields = {"slug": ("name",)}
    inlines = [ProductImageInline]


@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ("image_label", "color", "is_main")
    list_filter = ("product", "color", "is_main")
    search_fields = ("product__name",)

    def image_label(self, obj):
        """
        Показываем в списке:
         - имя товара,
         - 'Front' если is_main=True, иначе 'Back',
         - имя цвета (или 'no-color')
        """
        angle = "Front" if obj.is_main else "Back"
        color_name = obj.color.name if obj.color else "no-color"
        return f"{obj.product.name} – {angle} – {color_name}"

    image_label.short_description = "Image"

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'first_name', 'last_name', 'status', 'created')
    list_filter  = ('status',)
    search_fields = ('first_name', 'last_name', 'email')
    
@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'product', 'qty', 'price')

@admin.register(PromoCode)
class PromoCodeAdmin(admin.ModelAdmin):
    list_display = ('code', 'type', 'discount', 'active', 'valid_from', 'valid_to')
    list_filter  = ('type', 'active')
    search_fields = ('code',)