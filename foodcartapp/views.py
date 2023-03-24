from rest_framework.decorators import api_view
from django.http import JsonResponse
from rest_framework.response import Response
from django.templatetags.static import static
from rest_framework.serializers import ModelSerializer

from .models import Product, Order, OrderProduct



def banners_list_api(request):
    # FIXME move data to db?
    return JsonResponse([
        {
            'title': 'Burger',
            'src': static('burger.jpg'),
            'text': 'Tasty Burger at your door step',
        },
        {
            'title': 'Spices',
            'src': static('food.jpg'),
            'text': 'All Cuisines',
        },
        {
            'title': 'New York',
            'src': static('tasty.jpg'),
            'text': 'Food is incomplete without a tasty dessert',
        }
    ], safe=False, json_dumps_params={
        'ensure_ascii': False,
        'indent': 4,
    })

@api_view(['GET'])
def product_list_api(request):
    products = Product.objects.select_related('category').available()

    dumped_products = []
    for product in products:
        dumped_product = {
            'id': product.id,
            'name': product.name,
            'price': product.price,
            'special_status': product.special_status,
            'description': product.description,
            'category': {
                'id': product.category.id,
                'name': product.category.name,
            } if product.category else None,
            'image': product.image.url,
            'restaurant': {
                'id': product.id,
                'name': product.name,
            }
        }
        dumped_products.append(dumped_product)
    return Response(dumped_products)


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


@api_view(['POST'])
def register_order(request):
    serializer = OrderSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    order_info = serializer.validated_data
    # try:
    #     client_phone = phonenumbers.parse(order_info['phonenumber'], 'RU')
    #     if phonenumbers.is_valid_number(client_phone):
    #         phonenumber = order_info['phonenumber']
    #     else:
    #         return Response({'phonenumber': 'Введен некорректный номер телефона'})
    # except:
    #     return Response({'phonenumber': 'Введен некорректный номер телефона'})

    order = Order.objects.create(
        firstname=order_info['firstname'],
        lastname=order_info['lastname'],
        phonenumber=order_info['phonenumber'],
        address=order_info['address'],
    )

    for product_param in order_info['products']:
        product_name = product_param.get('product')
        product = Product.objects.get(name=product_name)
        order_elements = OrderProduct.objects.create(
            order=order,
            product=product,
            quantity=product_param['quantity']
        )

    serializer = OrderSerializer(order)
    return Response(serializer.data, status=200)
