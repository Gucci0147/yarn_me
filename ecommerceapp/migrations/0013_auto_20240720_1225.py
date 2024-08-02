# Generated by Django 3.2.1 on 2024-07-20 11:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ecommerceapp', '0012_alter_order_payment_method'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='paystack_reference',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='order',
            name='order_status',
            field=models.CharField(default='Order Received', max_length=50),
        ),
    ]
