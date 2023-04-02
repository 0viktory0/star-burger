import requests

from django.conf import settings
from django.db import transaction
from rest_framework.serializers import ModelSerializer

from .models import Order, OrderProduct
from geoapp.models import Place
from geoapp.geocoding import fetch_coordinates


class OrderProductSerializer(ModelSerializer):
    class Meta:
        model = OrderProduct
        fields = ['product', 'quantity']


class OrderSerializer(ModelSerializer):
    products = OrderProductSerializer(many=True,
                                       allow_empty=False,
                                       write_only=True)

    class Meta:
        model = Order
        fields = ['id', 'firstname', 'lastname', 'address', 'phonenumber', 'products']

    @transaction.atomic
    def create(self, validated_data):
        order = Order.objects.create(
            firstname=validated_data['firstname'],
            lastname=validated_data['lastname'],
            phonenumber=validated_data['phonenumber'],
            address=validated_data['address'],
        )
        products = validated_data['products']
        elements = [OrderProduct(
            order=order,
            price=fields['product'].price,
            **fields
        ) for fields in products]
        OrderProduct.objects.bulk_create(elements)

        address, status = Place.objects.get_or_create(
            address=validated_data['address'],
        )
        if not address.lat or not address.lon:
            try:
                address.lat, address.lon = fetch_coordinates(
                    settings.YANDEX_API_KEY,
                    validated_data['address'],
                )
            except (requests.exceptions.HTTPError, KeyError) as error:
                pass
            address.save()
        return order

