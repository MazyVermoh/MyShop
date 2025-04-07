from store.models import Product, Color, Size

products_data = [
    {
        "name": "Футболка Lionel Messi",
        "slug": "lionel-messi",
        "price": 3490.00,
        "description": "Описание футболки Lionel Messi",
        "additional_info": "Дополнительная информация по Messi",
        "image": "products/Messi.PNG"  # Путь внутри MEDIA_ROOT
    },
    {
        "name": "Футболка Cristiano Ronaldo",
        "slug": "cristiano-ronaldo",
        "price": 3490.00,
        "description": "Описание футболки Cristiano Ronaldo",
        "additional_info": "Дополнительная информация по Ronaldo",
        "image": "products/Ronaldo.PNG"
    },
    # ... добавьте ещё товары ...
]

def run():
    # Создаём несколько цветов
    white_color, _ = Color.objects.get_or_create(name='Белый', code='#FFFFFF')
    cream_color, _ = Color.objects.get_or_create(name='Бежевый', code='#F5F5DC')
    black_color, _ = Color.objects.get_or_create(name='Чёрный', code='#000000')

    # Создаём несколько размеров
    s_size, _ = Size.objects.get_or_create(name='S')
    m_size, _ = Size.objects.get_or_create(name='M')
    l_size, _ = Size.objects.get_or_create(name='L')
    xl_size, _ = Size.objects.get_or_create(name='XL')

    for prod_data in products_data:
        product, created = Product.objects.get_or_create(
            slug=prod_data['slug'],
            defaults={
                'name': prod_data['name'],
                'price': prod_data['price'],
                'description': prod_data['description'],
                'additional_info': prod_data['additional_info'],
                'image': prod_data['image']
            }
        )
        if created:
            print(f"Создан товар: {product.name}")
        else:
            print(f"Товар {product.name} уже существует, пропускаем.")

        # Привязываем доступные цвета/размеры
        product.colors.set([white_color, cream_color, black_color])  
        product.sizes.set([s_size, m_size, l_size, xl_size])
        product.save()

    print("Данные о товарах успешно загружены!")