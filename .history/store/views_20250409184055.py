from django.shortcuts import render, get_object_or_404
from .models import Product
import random

def index(request):
    # Загружаем все товары из базы
    products = Product.objects.all()
    context = {
        'products': products
    }
    return render(request, 'store/index.html', context)

def collections_goat(request):
    # Ручное задание slug-ов товаров для коллекции G.O.A.T
    goat_slugs = ['lionel-messi', 'cristiano-ronaldo']  # Замените или дополните по необходимости
    products = Product.objects.filter(slug__in=goat_slugs)
    context = {
        'products': products
    }
    return render(request, 'store/collections_goat.html', context)

def collections_elite(request):
    # Ручное задание slug-ов товаров для коллекции Elite
    elite_slugs = ['neymar']  # Замените или дополните по необходимости
    products = Product.objects.filter(slug__in=elite_slugs)
    context = {
        'products': products
    }
    return render(request, 'store/collections_elite.html', context)

def collections_legends(request):
    # Ручное задание slug-ов товаров для коллекции Legends
    legends_slugs = ['jude-bellingham']  # Замените или дополните по необходимости
    products = Product.objects.filter(slug__in=legends_slugs)
    context = {
        'products': products
    }
    return render(request, 'store/collections_legends.html', context)

def kids_goat(request):
    # Если для детских товаров необходимо, можно задать список slug-ов
    kids_goat_slugs = []  # Заполните, если есть товары для детской коллекции G.O.A.T
    products = Product.objects.filter(slug__in=kids_goat_slugs)
    context = {
        'products': products
    }
    return render(request, 'store/kids_goat.html', context)

def kids_elite(request):
    kids_elite_slugs = []  # Заполните при наличии
    products = Product.objects.filter(slug__in=kids_elite_slugs)
    context = {
        'products': products
    }
    return render(request, 'store/kids_elite.html', context)

def kids_legends(request):
    kids_legends_slugs = []  # Заполните при наличии
    products = Product.objects.filter(slug__in=kids_legends_slugs)
    context = {
        'products': products
    }
    return render(request, 'store/kids_legends.html', context)

def promotions(request):
    promotions_slugs = []  # Заполните, если используются
    products = Product.objects.filter(slug__in=promotions_slugs)
    context = {
        'products': products
    }
    return render(request, 'store/promotions.html', context)

def giftcards(request):
    giftcards_slugs = []  # Заполните, если применимо
    products = Product.objects.filter(slug__in=giftcards_slugs)
    context = {
        'products': products
    }
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
    Все фото берем из product.images через свойство main_photo/second_photo.
    """
    product = get_object_or_404(Product, slug=slug)

    # Генерируем 3 случайных рекомендованных товара,
    # исключая текущий товар.
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