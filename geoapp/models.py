from django.db import models


class Place(models.Model):
    address = models.CharField(
        'Адрес',
        max_length=100,
        unique=True,
        db_index=True,
    )
    lon = models.CharField(
        'Долгота',
        max_length=10,
        blank=True,
    )
    lat = models.CharField(
        'Широта',
        max_length=10,
        blank=True,
    )
    request_date = models.DateField(
        'Дата последнего запроса к Геокодеру',
        blank=True,
        null=True,
    )
