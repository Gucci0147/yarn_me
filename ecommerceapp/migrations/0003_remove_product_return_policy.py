# Generated by Django 3.2.1 on 2024-03-29 14:51

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ecommerceapp', '0002_remove_product_warranty'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='product',
            name='return_policy',
        ),
    ]
