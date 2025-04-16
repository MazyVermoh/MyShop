from django.shortcuts import render, get_object_or_404
from .models import Product
import random

def index(request):
    # Задаём явный порядок товаров через список slug'ов
    product_order = [
        'lionel-messi',            # 1. Messi
        'cristiano-ronaldo',        # 2. Cristiano Ronaldo
        'neymar',                   # 3. Neymar
        'kylian-mbappe',            # 4. Mbappe
        'jude-bellingham',          # 5. Bellingham
        'ronaldinho',               # 6. Ronaldinho
        'karim-benzema',            # 7. Benzema
        'zlatan-ibrahimovic'        # 8. Zlatan Ibrahimovic
    ]
    products = []
    for slug in product_order:
        try:
            product = Product.objects.get(slug=slug)
            products.append(product)
        except Product.DoesNotExist:
            pass

    context = {
        'products': products
    }
    return render(request, 'store/index.html', context)

def collections_goat(request):
    # Пример: для коллекции G.O.A.T. задаём вручную список slug'ов
    goat_slugs = ['lionel-messi', 'cristiano-ronaldo']
    products = Product.objects.filter(slug__in=goat_slugs)
    context = {
        'products': products
    }
    return render(request, 'store/collections_goat.html', context)

def collections_elite(request):
    # Коллекция Elite: 1. Mbappe, 2. Neymar, 3. Bellingham
    elite_slugs = ['kylian-mbappe', 'neymar', 'jude-bellingham']
    products = Product.objects.filter(slug__in=elite_slugs)
    context = {
        'products': products
    }
    return render(request, 'store/collections_elite.html', context)

def collections_legends(request):
    # Коллекция Legends: 1. Cristiano Ronaldo, 2. Benzema, 3. Zlatan Ibrahimovic
    legends_slugs = ['ronaldinho', 'karim-benzema', 'zlatan-ibrahimovic']
    products = Product.objects.filter(slug__in=legends_slugs)
    context = {
        'products': products
    }
    return render(request, 'store/collections_legends.html', context)

def kids_goat(request):
    kids_goat_slugs = []  # Заполните, если есть товары для детской коллекции G.O.A.T.
    products = Product.objects.filter(slug__in=kids_goat_slugs)
    context = {'products': products}
    return render(request, 'store/kids_goat.html', context)

def kids_elite(request):
    kids_elite_slugs = []  # Заполните, если есть товары для детской коллекции Elite
    products = Product.objects.filter(slug__in=kids_elite_slugs)
    context = {'products': products}
    return render(request, 'store/kids_elite.html', context)

def kids_legends(request):
    kids_legends_slugs = []  # Заполните, если есть товары для детской коллекции Legends
    products = Product.objects.filter(slug__in=kids_legends_slugs)
    context = {'products': products}
    return render(request, 'store/kids_legends.html', context)

def promotions(request):
    promotions_slugs = []  # Заполните, если используются
    products = Product.objects.filter(slug__in=promotions_slugs)
    context = {'products': products}
    return render(request, 'store/promotions.html', context)

def giftcards(request):
    giftcards_slugs = []  # Заполните, если применимо
    products = Product.objects.filter(slug__in=giftcards_slugs)
    context = {'products': products}
    return render(request, 'store/giftcards.html', context)

def contacts(request):
    return render(request, 'store/contacts.html')

def about(request):
    return render(request, 'store/about.html')

def social(request):
    return render(request, 'store/social.html')

def product_detail(request, slug):
    """
    Детальная страница товара.
    Все фото берем через свойства main_photo и second_photo.
    """
    product = get_object_or_404(Product, slug=slug)

    # Генерируем 3 рекомендованных товара, исключая текущий
    products_count = Product.objects.count()
    if products_count > 1:
        recommended = Product.objects.exclude(id=product.id).order_by('?')[:3]
    else:
        recommended = []

    context = {
        'product': product,
        'recommended_products': recommended
    }
    return render(request, 'store/product_detail.html', context)