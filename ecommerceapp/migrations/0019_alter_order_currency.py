# Generated by Django 3.2.1 on 2024-07-25 09:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ecommerceapp', '0018_alter_order_currency'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='currency',
            field=models.CharField(choices=[('USD', 'Dollar'), ('EUR', 'Euro'), ('NGN', 'Naira'), ('CAD', 'Canadian Dollar'), ('AUD', 'Australian Dollar')], max_length=3),
        ),
    ]
