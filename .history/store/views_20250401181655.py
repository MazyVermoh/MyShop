from django.shortcuts import render, get_object_or_404
from .models import Product
import random

def index(request):
    return render(request, 'store/index.html')

def collections_goat(request):
    return render(request, 'store/collections_goat.html')

def collections_elite(request):
    return render(request, 'store/collections_elite.html')

def collections_legends(request):
    return render(request, 'store/collections_legends.html')

def kids_goat(request):
    return render(request, 'store/kids_goat.html')

def kids_elite(request):
    return render(request, 'store/kids_elite.html')

def kids_legends(request):
    return render(request, 'store/kids_legends.html')

def promotions(request):
    return render(request, 'store/promotions.html')

def giftcards(request):
    return render(request, 'store/giftcards.html')

def contacts(request):
    return render(request, 'store/contacts.html')

def about(request):
    return render(request, 'store/about.html')

def social(request):
    return render(request, 'store/social.html')

def product_detail(request, slug):
    """
    Страница детального просмотра товара.
    """
    product = get_object_or_404(Product, slug=slug)

    # Выбираем несколько случайных товаров, исключая текущий
    # По желанию можно менять логику (по категориям и т.д.)
    products_count = Product.objects.count()
    if products_count > 1:
        recommended = Product.objects.exclude(id=product.id).order_by('?')[:3]
    else:
        recommended = []

    context = {
        'product': product,
        'recommended_products': recommended
    }
    return render(request, 'store/product_detail_messi.html', context)