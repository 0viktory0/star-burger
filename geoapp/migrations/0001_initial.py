# Generated by Django 3.2.15 on 2023-03-28 18:22

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Place',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('address', models.CharField(db_index=True, max_length=100, unique=True, verbose_name='Адрес')),
                ('lon', models.CharField(blank=True, max_length=10, null=True, verbose_name='Долгота')),
                ('lat', models.CharField(blank=True, max_length=10, null=True, verbose_name='Широта')),
                ('request_date', models.DateField(blank=True, null=True, verbose_name='Дата последнего запроса к Геокодеру')),
            ],
        ),
    ]
