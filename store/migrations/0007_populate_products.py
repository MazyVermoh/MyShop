from django.db import migrations

def create_products(apps, schema_editor):
    Product = apps.get_model('store', 'Product')
    Size = apps.get_model('store', 'Size')
    
    # Получаем размеры S, M, L, XL из базы данных.
    sizes = list(Size.objects.filter(name__in=['S', 'M', 'L', 'XL']))
    
    products_data = [
        {"slug": "lionel-messi", "name": "Lionel Messi"},
        {"slug": "cristiano-ronaldo", "name": "Cristiano Ronaldo"},
        {"slug": "neymar", "name": "Neymar"},
        {"slug": "kylian-mbappe", "name": "Kylian Mbappe"},
        {"slug": "jude-bellingham", "name": "Jude Bellingham"},
        {"slug": "ronaldinho", "name": "Ronaldinho"},
        {"slug": "karim-benzema", "name": "Karim Benzema"},
        {"slug": "zlatan-ibrahimovic", "name": "Zlatan Ibrahimovic"},
    ]
    
    for pdata in products_data:
        product, created = Product.objects.get_or_create(
            slug=pdata["slug"],
            defaults={
                "name": pdata["name"],
                "price": 3490,
                "description": "Описание отсутствует.",
                "additional_info": "Дополнительная информация отсутствует."
            }
        )
        if created:
            # Привязываем ко всем созданным товарам все размеры S, M, L, XL.
            product.sizes.set(sizes)

def reverse_products(apps, schema_editor):
    Product = apps.get_model('store', 'Product')
    slugs = [
        'lionel-messi', 'cristiano-ronaldo', 'neymar', 'kylian-mbappe',
        'jude-bellingham', 'ronaldinho', 'karim-benzema', 'zlatan-ibrahimovic'
    ]
    Product.objects.filter(slug__in=slugs).delete()

class Migration(migrations.Migration):

    dependencies = [
        ('store', '0006_remove_product_colors_alter_product_sizes_and_more'),
    ]

    operations = [
        migrations.RunPython(create_products, reverse_products),
    ]