from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse, Http404
from django.db.models import Prefetch                       # ← NEW
from .models import Product, Color, ProductImage            # ← NEW
import random


def index(request):
    """
    Главная: необязательный GET‑параметр ?color=<id>
    • нет параметра  → показываем «промо»‑сортировку;
    • есть параметр → отфильтровываем товары, у которых
                      есть фотография нужного цвета.
    """
    color_id = request.GET.get("color")            # str | None

    # базовый queryset с prefetch (ускоряет базу)
    base_qs = Product.objects.prefetch_related(
        Prefetch("images", queryset=ProductImage.objects.select_related("color")),
        "colors",
        "sizes",
    )

    if color_id:
        base_qs = (
            base_qs
            .filter(
                colors__id=color_id,          # товар связан с цветом
                images__color_id=color_id,    # и для него есть фото такого цвета
            )
            .distinct()
            .order_by("id")                   # любая стабильная сортировка
        )
    else:
        order = [
            "lionel-messi", "cristiano-ronaldo", "neymar",
            "kylian-mbappe", "jude-bellingham", "ronaldinho",
            "karim-benzema", "zlatan-ibrahimovic",
        ]
        base_qs = sorted(base_qs.filter(slug__in=order), key=lambda p: order.index(p.slug))

    context = {
        "products": base_qs,
        "selected_color": int(color_id) if color_id else None,
    }
    return render(request, "store/index.html", context)


# ---- коллекции / детские / акции (оставил как у тебя) ------------------
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


def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug)
    recommended = Product.objects.exclude(id=product.id).order_by("?")[:3]
    return render(request, "store/product_detail.html",
                  {"product": product, "recommended_products": recommended})


# ---------- AJAX: первая картинка заданного цвета -----------------------
def product_first_image(request, prod_id, color_id):
    try:
        prod = Product.objects.get(id=prod_id)
    except Product.DoesNotExist:
        raise Http404
    img = prod.images.filter(color_id=color_id).order_by("id").first()
    return JsonResponse({"url": img.image.url if img else ""})