# Generated by Django 3.2.15 on 2023-03-25 13:15

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0041_alter_order_phonenumber'),
    ]

    operations = [
        migrations.AddField(
            model_name='orderproduct',
            name='price',
            field=models.DecimalField(decimal_places=2, default=1, max_digits=5, validators=[django.core.validators.MinValueValidator(0)], verbose_name='Цена товара'),
        ),
    ]
