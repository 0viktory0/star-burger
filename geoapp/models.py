from django.db import models


class Place(models.Model):
    address = models.CharField(
        'Адрес',
        max_length=100,
        unique=True,
        db_index=True,
    )
    lon = models.FloatField(
        verbose_name='Долгота',
        blank=True,
    )
    lat = models.FloatField(
        verbose_name='Широта',
        blank=True,
    )
    request_date = models.DateField(
        'Дата последнего запроса к Геокодеру',
        blank=True,
        null=True,
    )
