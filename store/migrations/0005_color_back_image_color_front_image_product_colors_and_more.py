# Generated by Django 5.2 on 2025-04-08 14:49

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("store", "0004_remove_product_back_image_remove_product_colors_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="color",
            name="back_image",
            field=models.ImageField(blank=True, null=True, upload_to="colors/"),
        ),
        migrations.AddField(
            model_name="color",
            name="front_image",
            field=models.ImageField(blank=True, null=True, upload_to="colors/"),
        ),
        migrations.AddField(
            model_name="product",
            name="colors",
            field=models.ManyToManyField(blank=True, to="store.color"),
        ),
        migrations.AddField(
            model_name="product",
            name="sizes",
            field=models.ManyToManyField(blank=True, to="store.size"),
        ),
    ]
