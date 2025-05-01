from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse, Http404
from django.db.models import Prefetch

from .models import Product, ProductImage, Color


# ---------------------------------------------------------------------
# Главная страница
# ---------------------------------------------------------------------
def index(request):
    """
    1) Для каждого продукта группируем изображения по цветам.
    2) По умолчанию — выбираем цвет “Белый” (если есть фото), иначе первый с фото.
    3) Формируем:
         p.filtered_images — список front/back именно этого цвета,
         p.swatches        — список {id, code, has_image, front_url, back_url}.
    """
    promo_order = [
        "lionel-messi", "cristiano-ronaldo", "neymar",
        "kylian-mbappe", "jude-bellingham", "ronaldinho",
        "karim-benzema", "zlatan-ibrahimovic",
    ]

    qs = Product.objects.prefetch_related(
        Prefetch("images", queryset=ProductImage.objects.select_related("color")),
        "colors", "sizes",
    )
    products = sorted(
        qs.filter(slug__in=promo_order),
        key=lambda p: promo_order.index(p.slug),
    )

    for p in products:
        # Группировка по цвету, сначала is_main=True
        by_color = {}
        for img in sorted(p.images.all(), key=lambda i: (-i.is_main, i.id)):
            by_color.setdefault(img.color_id, []).append(img)

        # Выбор default_color: сначала “Белый”, если фото, иначе первый с фото
        default_color = None
        for color in p.colors.all():
            if color.name.lower() == "белый" and by_color.get(color.id):
                default_color = color.id
                break
        if default_color is None:
            default_color = next((cid for cid, imgs in by_color.items() if imgs), None)

        # Список изображений для карусели
        p.filtered_images = by_color.get(default_color, [])

        # Подготовка swatches
        swatches = []
        for color in p.colors.all():
            imgs = by_color.get(color.id, [])
            swatches.append({
                "id":         color.id,
                "code":       (color.code or "#ffffff").lower(),
                "has_image": bool(imgs),
                "front_url":  imgs[0].image.url if len(imgs) > 0 else "",
                "back_url":   imgs[1].image.url if len(imgs) > 1 else "",
            })
        p.swatches = swatches

    return render(request, "store/index.html", {
        "products": products,
    })


# ---------------------------------------------------------------------
# Коллекции / детские / акции — без изменений
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
    """
    По аналогии с index: выбираем default_color (по GET?color=… или “Белый”),
    формируем filtered_images и swatches, передаем selected_color.
    """
    product = get_object_or_404(
        Product.objects.prefetch_related(
            Prefetch("images", queryset=ProductImage.objects.select_related("color")),
            "colors", "sizes",
        ),
        slug=slug
    )

    # Группировка по цвету
    by_color = {}
    for img in sorted(product.images.all(), key=lambda i: (-i.is_main, i.id)):
        by_color.setdefault(img.color_id, []).append(img)

    # Смотрим GET-параметр ?color=
    sel = request.GET.get("color")
    try:
        sel_id = int(sel)
    except (TypeError, ValueError):
        sel_id = None

    # Определяем default_color
    if sel_id in by_color and by_color[sel_id]:
        default_color = sel_id
    else:
        white = next(
            (c.id for c in product.colors.all() if c.name.lower() == "белый"),
            None
        )
        if white and by_color.get(white):
            default_color = white
        else:
            default_color = next((cid for cid, imgs in by_color.items() if imgs), None)

    # Формируем изображения для detail
    filtered = by_color.get(default_color, [])

    # Свотчи
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

    # Рекомендации
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