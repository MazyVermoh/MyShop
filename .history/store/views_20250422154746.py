from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse, Http404
from django.db.models import Prefetch

from .models import Product, Color, ProductImage


def index(request):
    """
    Главная.  ?color=<id> – фильтр по цвету.
    Для карточек формируем product.filtered_images:
      • если цвет выбран → только снимки этого цвета;
      • иначе → все снимки продукта.
    """
    color_id = request.GET.get("color")           # None или строка id

    base_qs = Product.objects.prefetch_related(
        Prefetch("images", queryset=ProductImage.objects.select_related("color")),
        "colors",
        "sizes",
    )

    if color_id:
        base_qs = (
            base_qs
            .filter(colors__id=color_id,
                    images__color_id=color_id)
            .distinct()
            .order_by("id")
        )
    else:
        promo_order = [
            "lionel-messi", "cristiano-ronaldo", "neymar",
            "kylian-mbappe", "jude-bellingham", "ronaldinho",
            "karim-benzema", "zlatan-ibrahimovic",
        ]
        base_qs = sorted(
            base_qs.filter(slug__in=promo_order),
            key=lambda p: promo_order.index(p.slug),
        )

    # ------------------------------------------------------------------
    #  Формируем filtered_images у каждого Product
    # ------------------------------------------------------------------
    for p in base_qs:
        if color_id:
            p.filtered_images = list(
                p.images
                 .filter(color_id=color_id)
                 .order_by("-is_main", "id")
            )
        else:
            p.filtered_images = list(p.images.all())

    context = {
        "products":       base_qs,
        "selected_color": int(color_id) if color_id else None,
    }
    return render(request, "store/index.html", context)


# ----------------------------------------------------------------------
# остальные вьюхи (collections_*, kids_*, product_detail и т. д.) остаются
# без изменений, их можно оставить как есть.
# ----------------------------------------------------------------------

def product_first_image(request, prod_id, color_id):
    try:
        prod = Product.objects.get(id=prod_id)
    except Product.DoesNotExist:
        raise Http404
    img = prod.images.filter(color_id=color_id).order_by("-is_main", "id").first()
    return JsonResponse({"url": img.image.url if img else ""})