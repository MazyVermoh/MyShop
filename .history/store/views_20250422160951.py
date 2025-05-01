from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse, Http404
from django.db.models import Prefetch

from .models import Product, Color, ProductImage


# ---------------------------------------------------------------------
# Главная страница
# ---------------------------------------------------------------------
def index(request):
    """
    Главная. Для каждого продукта готовим:
      1) filtered_images — все его изображения (front/back) для карусели;
      2) images_by_color — словарь: color_id → [отсортированные изображения этого цвета];
      3) swatches — список данных для каждой точки: id, code, has_image, front_url, back_url.
    """
    promo_order = [
        "lionel-messi", "cristiano-ronaldo", "neymar",
        "kylian-mbappe", "jude-bellingham", "ronaldinho",
        "karim-benzema", "zlatan-ibrahimovic",
    ]

    qs = Product.objects.prefetch_related(
        Prefetch("images", queryset=ProductImage.objects.select_related("color")),
        "colors",
        "sizes",
    )

    # Берём только промо‑товары в нужном порядке
    products = sorted(
        qs.filter(slug__in=promo_order),
        key=lambda p: promo_order.index(p.slug),
    )

    for p in products:
        # 1) группировка изображений по цвету (is_main=True первыми)
        by_color = {}
        for img in sorted(p.images.all(), key=lambda i: (-i.is_main, i.id)):
            by_color.setdefault(img.color_id, []).append(img)
        p.images_by_color = by_color

        # 2) полная карусель (front + back)
        p.filtered_images = sorted(p.images.all(), key=lambda i: (-i.is_main, i.id))

        # 3) подготовка данных для swatches
        swatches = []
        for color in p.colors.all():
            imgs = by_color.get(color.id, [])
            swatches.append({
                "id":         color.id,
                "code":       color.code or "#fff",
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
    product = get_object_or_404(
        Product.objects.prefetch_related(
            Prefetch("images", queryset=ProductImage.objects.select_related("color")),
            "colors",
            "sizes",
        ),
        slug=slug
    )

    # 1) сгруппировать картинки по цвету (is_main=True первыми)
    by_color = {}
    for img in sorted(product.images.all(), key=lambda i: (-i.is_main, i.id)):
        by_color.setdefault(img.color_id, []).append(img)

    # 2) выбрать «по умолчанию» белый цвет, если он есть
    try:
        white = Color.objects.get(name__iexact="Белый")
        default_color = white.id if white.id in by_color else next(iter(by_color.keys()))
    except Color.DoesNotExist:
        default_color = next(iter(by_color.keys()))

    # 3) картинки для текущей фильтрации
    filtered = by_color.get(default_color, [])

    # 4) формируем swatches
    swatches = []
    for color in product.colors.all():
        imgs = by_color.get(color.id, [])
        swatches.append({
            "id":         color.id,
            "code":       color.code or "#ffffff",
            "has_image": bool(imgs),
            "front_url":  imgs[0].image.url if len(imgs) > 0 else "",
            "back_url":   imgs[1].image.url if len(imgs) > 1 else "",
        })

    # 5) рекомендованные
    recommended = Product.objects.exclude(id=product.id).order_by("?")[:3]

    return render(request, "store/product_detail.html", {
        "product":         product,
        "filtered_images": filtered,
        "swatches":        swatches,
        "selected_color":  default_color,
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