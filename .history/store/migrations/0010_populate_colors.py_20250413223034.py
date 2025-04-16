from django.db import migrations

def create_colors(apps, schema_editor):
    Color = apps.get_model('store', 'Color')
    colors = [
        {"name": "Белый", "code": "#FFFFFF"},
        {"name": "Бежевый", "code": "#F5F5DC"},  # можно изменить по вкусу
        {"name": "Черный", "code": "#000000"}
    ]
    for color in colors:
        Color.objects.get_or_create(name=color["name"], defaults={"code": color["code"]})

def reverse_colors(apps, schema_editor):
    Color = apps.get_model('store', 'Color')
    color_names = ["Белый", "Бежевый", "Черный"]
    Color.objects.filter(name__in=color_names).delete()

class Migration(migrations.Migration):

    dependencies = [
        ('store', '0007_populate_products'),  # Зависимость должна ссылаться на последнюю миграцию
    ]

    operations = [
        migrations.RunPython(create_colors, reverse_colors),
    ]