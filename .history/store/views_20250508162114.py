from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse, Http404
from django.db.models import Prefetch

from .models import Product, ProductImage, Color
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt  # AJAX через fetch
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from .models import Subscriber
from .utils import send_subscribe_confirmation
from django.conf import settings

# ---------------------------------------------------------------------
# Главная страница
# ---------------------------------------------------------------------
def index(request):
    """
    Для каждого продукта:
      – группируем изображения по цветам,
      – выбираем default_color (“Белый” или первый с фото),
      – готовим p.filtered_images и p.swatches.
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
        by_color = {}
        for img in sorted(p.images.all(), key=lambda i: (-i.is_main, i.id)):
            by_color.setdefault(img.color_id, []).append(img)

        default_color = None
        for color in p.colors.all():
            if color.name.lower() == "белый" and by_color.get(color.id):
                default_color = color.id
                break
        if default_color is None:
            default_color = next((cid for cid, imgs in by_color.items() if imgs), None)

        p.filtered_images = by_color.get(default_color, [])

        swatches = []
        for color in p.colors.all():
            imgs = by_color.get(color.id, [])
            swatches.append({
                "id":        color.id,
                "code":      (color.code or "#ffffff").lower(),
                "has_image": bool(imgs),
                "front_url": imgs[0].image.url if len(imgs) > 0 else "",
                "back_url":  imgs[1].image.url if len(imgs) > 1 else "",
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
    return render(request, "store/kids_goat.html", {"products": Product.objects.none()})


def kids_elite(request):
    return render(request, "store/kids_elite.html", {"products": Product.objects.none()})


def kids_legends(request):
    return render(request, "store/kids_legends.html", {"products": Product.objects.none()})


def promotions(request):
    return render(request, "store/promotions.html", {"products": Product.objects.none()})


def giftcards(request):
    return render(request, "store/giftcards.html", {"products": Product.objects.none()})


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

    # Группируем по цвету
    by_color = {}
    for img in sorted(product.images.all(), key=lambda i: (-i.is_main, i.id)):
        by_color.setdefault(img.color_id, []).append(img)

    # Выбираем color из GET или default “Белый”
    sel_color = request.GET.get("color")
    try:
        sel_color = int(sel_color)
    except (TypeError, ValueError):
        sel_color = None
    if sel_color not in by_color or not by_color[sel_color]:
        white = next((c.id for c in product.colors.all() if c.name.lower() == "белый"), None)
        sel_color = white if white in by_color else next((cid for cid, imgs in by_color.items() if imgs), None)

    filtered = by_color.get(sel_color, [])

    swatches = []
    for color in product.colors.all():
        imgs = by_color.get(color.id, [])
        swatches.append({
            "id":        color.id,
            "code":      (color.code or "#ffffff").lower(),
            "has_image": bool(imgs),
            "front_url": imgs[0].image.url if len(imgs) > 0 else "",
            "back_url":  imgs[1].image.url if len(imgs) > 1 else "",
        })

    # Обработка размера из GET
    sel_size = request.GET.get("size")

    recommended = Product.objects.exclude(id=product.id).order_by("?")[:3]

    return render(request, "store/product_detail.html", {
        "product":              product,
        "filtered_images":      filtered,
        "swatches":             swatches,
        "selected_color":       sel_color,
        "selected_size":        sel_size,
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

@require_POST
@csrf_exempt  # если используете fetch без CSRF‑token; можно убрать и передавать токен в JS
def subscribe(request):
    email = request.POST.get("email", "").strip().lower()
    try:
        validate_email(email)
    except ValidationError:
        return JsonResponse({"ok": False, "error": "Некорректный email"}, status=400)

    sub, created = Subscriber.objects.get_or_create(email=email)
    if sub.confirmed:
        return JsonResponse({"ok": True, "message": "Вы уже подписаны!"})
    # отправляем (повторно) письмо подтверждения
    send_subscribe_confirmation(sub)
    return JsonResponse({"ok": True, "message": "Ссылка для подтверждения отправлена на почту"})


def subscribe_confirm(request, sub_id, token):
    sub = get_object_or_404(Subscriber, id=sub_id)
    # очень простая проверка токена — в реальном проекте лучше хранить в БД
    import hashlib
    expected = hashlib.sha256(f"{sub.email}{settings.SECRET_KEY}".encode()).hexdigest()
    if token[:64] != expected[:64]:
        raise Http404

    sub.confirmed = True
    sub.save(update_fields=["confirmed"])
    return render(request, "store/subscribe_success.html")