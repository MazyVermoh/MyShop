from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse, Http404
from django.db.models import Prefetch

from .models import Product, Color, ProductImage
import random


# ---------------------------------------------------------------------
# Главная страница
# ---------------------------------------------------------------------
def index(request):
    """
    ?color=<id>  → показываем только товары, у которых есть
                   фотографии выбранного цвета, и в карусели выводим
                   только эти фотографии;
    без параметра → обычное промо‑упорядочение и все фото.
    """
    color_id = request.GET.get("color")          # None или строка

    base_qs = Product.objects.prefetch_related(
        Prefetch(
            "images",
            queryset=ProductImage.objects.select_related("color")
        ),
        "colors",
        "sizes",
    )

    if color_id:
        base_qs = (
            base_qs
            .filter(colors__id=color_id, images__color_id=color_id)
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

    # добавляем helper‑атрибуты каждому продукту
    for p in base_qs:
        # 1) какие цвета вообще есть у фотографий товара
        p.image_color_ids = {img.color_id for img in p.images.all() if img.color_id}

        # 2) снимки для текущего фильтра
        if color_id:
            p.filtered_images = list(
                p.images.filter(color_id=color_id).order_by("-is_main", "id")
            )
        else:
            p.filtered_images = list(p.images.all())

    context = {
        "products":       base_qs,
        "selected_color": int(color_id) if color_id else None,
    }
    return render(request, "store/index.html", context)


# ---------------------------------------------------------------------
# Коллекции / детские / акции — оставлены как были
# ---------------------------------------------------------------------
def collections_goat(request):
    slugs = ["lionel-messi", "cristiano-ronaldo"]
    return render(request, "store/collections_goat.html",
                  {"products": Product.objects.filter(slug__in=slugs)})


def collections_elite(request):
    slugs = ["kylian-mbappe", "neymar", "jude-bellingham"]
    return render(request, "store/collections_elite.html",
                  {"products": Product.objects.filter(slug__in=slugs)})


def collections_legends(request):
    slugs = ["ronaldinho", "karim-benzema", "zlatan-ibrahimovic"]
    return render(request, "store/collections_legends.html",
                  {"products": Product.objects.filter(slug__in=slugs)})


def kids_goat(request):
    return render(request, "store/kids_goat.html",
                  {"products": Product.objects.none()})


def kids_elite(request):
    return render(request, "store/kids_elite.html",
                  {"products": Product.objects.none()})


def kids_legends(request):
    return render(request, "store/kids_legends.html",
                  {"products": Product.objects.none()})


def promotions(request):
    return render(request, "store/promotions.html",
                  {"products": Product.objects.none()})


def giftcards(request):
    return render(request, "store/giftcards.html",
                  {"products": Product.objects.none()})


def contacts(request):
    return render(request, "store/contacts.html")


def about(request):
    return render(request, "store/about.html")


def social(request):
    return render(request, "store/social.html")


# ---------------------------------------------------------------------
# Детальная страница товара
# ---------------------------------------------------------------------
def product_detail(request, slug):
    product = get_object_or_404(
        Product.objects.prefetch_related(
            Prefetch("images", queryset=ProductImage.objects.select_related("color")),
            "colors", "sizes",
        ),
        slug=slug
    )

    # 1) сгруппировать изображения по цвету (is_main=True первыми)
    by_color = {}
    for img in sorted(product.images.all(), key=lambda i: (-i.is_main, i.id)):
        by_color.setdefault(img.color_id, []).append(img)

    # 2) построить список swatches
    swatches = []
    for color in product.colors.all():
        imgs = by_color.get(color.id, [])
        swatches.append({
            "id":         color.id,
            "code":       (color.code or "#ffffff").lower(),
            "has_image": bool(imgs),
            "front_url":  imgs[0].image.url if len(imgs) > 0 else "",
            "back_url":   imgs[1].image.url if len(imgs) > 1 else "",
        })

    # 3) найти белый swatch как default, иначе первый с фото
    white_id = next(
        (sw["id"] for sw in swatches if sw["code"] in ("#fff", "#ffffff")),
        None
    )
    if white_id and by_color.get(white_id):
        default_color = white_id
    else:
        default_color = next(
            (sw["id"] for sw in swatches if sw["has_image"]),
            swatches[0]["id"]
        )

    # 4) отфильтрованные картинки по default_color
    filtered = by_color.get(default_color, [])

    # 5) рекомендованные товары
    recommended = Product.objects.exclude(id=product.id).order_by("?")[:3]

    return render(request, "store/product_detail.html", {
        "product":             product,
        "filtered_images":     filtered,
        "swatches":            swatches,
        "selected_color":      default_color,
        "recommended_products": recommended,
    })


# ---------------------------------------------------------------------
# AJAX‑handler: первая картинка заданного цвета
# ---------------------------------------------------------------------
def product_first_image(request, prod_id, color_id):
    try:
        prod = Product.objects.get(id=prod_id)
    except Product.DoesNotExist:
        raise Http404
    img = prod.images.filter(color_id=color_id).order_by("-is_main", "id").first()
    return JsonResponse({"url": img.image.url if img else ""})