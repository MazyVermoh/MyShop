# Generated by Django 5.2 on 2025-04-13 20:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0007_populate_products'),
    ]

    operations = [
        migrations.CreateModel(
            name='Color',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, unique=True)),
                ('code', models.CharField(blank=True, max_length=7, null=True)),
            ],
        ),
    ]
