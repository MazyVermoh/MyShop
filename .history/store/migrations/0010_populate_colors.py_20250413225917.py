from django.db import migrations

def create_colors(apps, schema_editor):
    Color = apps.get_model('store', 'Color')
    colors = [
        {"name": "Белый", "code": "#FFFFFF"},
        {"name": "Бежевый", "code": "#F5F5DC"},  # по вкусу можно изменить
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
        ('store', '0008_readd_color'),  # Укажите точное имя миграции, созданной на Шаге 1
    ]

    operations = [
        migrations.RunPython(create_colors, reverse_colors),
    ]