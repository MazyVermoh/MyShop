# store/views.py
from __future__ import annotations

from django.conf import settings
from django.core.mail import send_mail
from django.db.models import Prefetch
from django.http import Http404, JsonResponse
from django.shortcuts import get_object_or_404, render
from django.views.decorators.http import require_POST

from .forms import SubscribeForm
from .models import Color, Product, ProductImage, Subscriber


# ---------------------------------------------------------------------
# Главная страница
# ---------------------------------------------------------------------
def index(request):
    """
    Формируем витрину: для каждого продукта группируем картинки по цветам,
    выбираем «Белый» (если есть) или первый цвет с фотографией.
    В результате у каждого Product появятся:
        p.filtered_images  — список картинок выбранного цвета
        p.swatches         — данные для цветных свотчей
    """
    promo_order = [
        "lionel-messi", "cristiano-ronaldo", "neymar",
        "kylian-mbappe", "jude-bellingham", "ronaldinho",
        "karim-benzema", "zlatan-ibrahimovic", "lamine-yamal", 
        "sergio-ramos", "zenidine-zidane", "ronaldo-nazario",
    ]

    qs = Product.objects.prefetch_related(
        Prefetch("images", queryset=ProductImage.objects.select_related("color")),
        "colors",
        "sizes",
    )
    products = sorted(
        qs.filter(slug__in=promo_order),
        key=lambda p: promo_order.index(p.slug),
    )

    for p in products:
        # группируем картинки по цвету
        by_color: dict[int, list[ProductImage]] = {}
        for img in sorted(p.images.all(), key=lambda i: (-i.is_main, i.id)):
            by_color.setdefault(img.color_id, []).append(img)

        # default_color = «Белый» или первый цвет, у которого есть фото
        default_color = next(
            (
                color.id
                for color in p.colors.all()
                if color.name.lower() == "белый" and by_color.get(color.id)
            ),
            None,
        ) or next((cid for cid, imgs in by_color.items() if imgs), None)

        p.filtered_images = by_color.get(default_color, [])

        # swatches
        swatches = []
        for color in p.colors.all():
            imgs = by_color.get(color.id, [])
            swatches.append(
                {
                    "id": color.id,
                    "code": (color.code or "#ffffff").lower(),
                    "has_image": bool(imgs),
                    "front_url": imgs[0].image.url if len(imgs) > 0 else "",
                    "back_url": imgs[1].image.url if len(imgs) > 1 else "",
                }
            )
        p.swatches = swatches

    return render(request, "store/index.html", {"products": products})


# ---------------------------------------------------------------------
# Коллекции / детские / акции
# ---------------------------------------------------------------------
def collections_goat(request):
    slugs = ["lionel-messi", "cristiano-ronaldo"]
    return render(
        request,
        "store/collections_goat.html",
        {"products": Product.objects.filter(slug__in=slugs)},
    )


def collections_elite(request):
    slugs = ["kylian-mbappe", "neymar", "jude-bellingham"]
    return render(
        request,
        "store/collections_elite.html",
        {"products": Product.objects.filter(slug__in=slugs)},
    )


def collections_legends(request):
    slugs = ["ronaldinho", "karim-benzema", "zlatan-ibrahimovic"]
    return render(
        request,
        "store/collections_legends.html",
        {"products": Product.objects.filter(slug__in=slugs)},
    )


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


# ---------------------------------------------------------------------
# Статические страницы
# ---------------------------------------------------------------------
def contacts(request):
    return render(request, "store/contacts.html")


def about(request):
    """Страница «О бренде» (шаблон templates/store/about.html)."""
    return render(request, "store/about.html")


def social(request):
    return render(request, "store/social.html")

def delivery(request):
    return render(request, "store/delivery.html")

def returns(request):
    return render(request, "store/returns.html")

def terms(request):
    return render(request, "store/terms.html")

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
        slug=slug,
    )

    # группируем картинки по цвету
    by_color: dict[int, list[ProductImage]] = {}
    for img in sorted(product.images.all(), key=lambda i: (-i.is_main, i.id)):
        by_color.setdefault(img.color_id, []).append(img)

    # выбранный цвет из GET или default “Белый”
    sel_color = request.GET.get("color")
    try:
        sel_color = int(sel_color)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        sel_color = None

    if sel_color not in by_color or not by_color[sel_color]:
        white = next(
            (c.id for c in product.colors.all() if c.name.lower() == "белый"), None
        )
        sel_color = white if white in by_color else next(
            (cid for cid, imgs in by_color.items() if imgs), None
        )

    filtered = by_color.get(sel_color, [])

    swatches = []
    for color in product.colors.all():
        imgs = by_color.get(color.id, [])
        swatches.append(
            {
                "id": color.id,
                "code": (color.code or "#ffffff").lower(),
                "has_image": bool(imgs),
                "front_url": imgs[0].image.url if len(imgs) > 0 else "",
                "back_url": imgs[1].image.url if len(imgs) > 1 else "",
            }
        )

    # выбранный размер из GET
    sel_size = request.GET.get("size")

    recommended = Product.objects.exclude(id=product.id).order_by("?")[:3]

    return render(
        request,
        "store/product_detail.html",
        {
            "product": product,
            "filtered_images": filtered,
            "swatches": swatches,
            "selected_color": sel_color,
            "selected_size": sel_size,
            "recommended_products": recommended,
        },
    )


# ---------------------------------------------------------------------
# AJAX-handler: картинка для свотча
# ---------------------------------------------------------------------
def product_first_image(request, prod_id, color_id):
    try:
        prod = Product.objects.get(id=prod_id)
    except Product.DoesNotExist:
        raise Http404

    img = prod.images.filter(color_id=color_id).order_by("-is_main", "id").first()
    return JsonResponse({"url": img.image.url if img else ""})


# ---------------------------------------------------------------------
# AJAX-handler: подписка
# ---------------------------------------------------------------------
@require_POST
def subscribe(request):
    """
    Принимает email, сохраняет в БД, шлёт welcome-письмо, возвращает JSON.
    """
    form = SubscribeForm(request.POST)
    if not form.is_valid():
        return JsonResponse({"status": "error", "errors": form.errors}, status=400)

    email = form.cleaned_data["email"]
    sub, created = Subscriber.objects.get_or_create(
        email=email,
        defaults={"confirmed": True},  # уберите confirmed для double-opt-in
    )

    # welcome-письмо только новым подписчикам
    if created:
        send_mail(
            subject="Спасибо за подписку на ABUZADA STORE!",
            message=(
                "Теперь вы будете первыми узнавать о новинках\n"
                "и получать персональные предложения.\n\n"
                "Если письмо попало в спам — добавьте нас в контакты."
            ),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
            fail_silently=True,  # чтобы подписка не падала, даже если SMTP недоступен
        )

    return JsonResponse({"status": "ok"})