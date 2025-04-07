from store.models import Product

products_data = [
    {
        "name": "Футболка Lionel Messi",
        "slug": "lionel-messi",
        "price": 3490.00,
        "description": "Описание футболки Lionel Messi",
        "image": "store/images/Messi.PNG"
    },
    {
        "name": "Футболка Cristiano Ronaldo",
        "slug": "cristiano-ronaldo",
        "price": 3490.00,
        "description": "Описание футболки Cristiano Ronaldo",
        "image": "store/images/Ronaldo.PNG"
    },
    {
        "name": "Футболка Neymar",
        "slug": "neymar",
        "price": 3490.00,
        "description": "Описание футболки Neymar",
        "image": "store/images/Neymar.PNG"
    },
    {
        "name": "Футболка Kylian Mbappe",
        "slug": "kylian-mbappe",
        "price": 3490.00,
        "description": "Описание футболки Kylian Mbappe",
        "image": "store/images/Mbappe.PNG"
    },
    {
        "name": "Футболка Jude Bellingham",
        "slug": "jude-bellingham",
        "price": 3490.00,
        "description": "Описание футболки Jude Bellingham",
        "image": "store/images/Bellingham.PNG"
    },
    {
        "name": "Футболка Ronaldinho",
        "slug": "ronaldinho",
        "price": 3490.00,
        "description": "Описание футболки Ronaldinho",
        "image": "store/images/Ronaldinho.PNG"
    },
    {
        "name": "Футболка Zlatan Ibrahimovic",
        "slug": "zlatan-ibrahimovic",
        "price": 3490.00,
        "description": "Описание футболки Zlatan Ibrahimovic",
        "image": "store/images/Zlatan.PNG"
    },
    {
        "name": "Футболка Karim Benzema",
        "slug": "karim-benzema",
        "price": 3490.00,
        "description": "Описание футболки Karim Benzema",
        "image": "store/images/Benzema.PNG"
    },
]

for prod_data in products_data:
    Product.objects.create(**prod_data)

print("Продукты успешно добавлены!")