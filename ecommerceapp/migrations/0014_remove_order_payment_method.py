# Generated by Django 3.2.1 on 2024-07-20 11:30

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ecommerceapp', '0013_auto_20240720_1225'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='order',
            name='payment_method',
        ),
    ]
