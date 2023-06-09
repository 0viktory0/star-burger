# Generated by Django 3.2.15 on 2023-03-25 14:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0042_orderproduct_price'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='status',
            field=models.CharField(choices=[('new', 'Необработанный'), ('cooking', 'Готовится'), ('delivering', 'Доставляется'), ('completed', 'Выполнен')], db_index=True, default='Необработанный', max_length=20, verbose_name='Статус заказа'),
        ),
    ]
