import json

from rest_framework.decorators import api_view
from django.http import JsonResponse
from rest_framework.response import Response
from django.templatetags.static import static

from .models import Product, Order, OrderProduct


from .models import Product


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

@api_view(['POST'])
def register_order(request):
    order_data = request.data
    order = Order.objects.create(
        firstname=order_data["firstname"],
        lastname=order_data["lastname"],
        phonenumber=order_data['phonenumber'],
        address=order_data['address'],
    )
    for product in order_data['products']:
        product_id = product.get('product')
        order_elements = OrderProduct.objects.create(
            order=order,
            product=Product.objects.get(id=product_id),
            quantity=product['quantity']
        )
    order_products = {
        'products': [product for product in order_data['products']],
        'firstname': order_data['firstname'],
        'lastname': order_data['lastname'],
        'phonenumber': order_data['phonenumber'],
        'address': order_data['address']
    }
    return Response(order_products)
