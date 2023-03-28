import requests
from geopy import distance

from django import forms
from django.shortcuts import redirect, render
from django.views import View
from django.urls import reverse_lazy
from django.utils import timezone
from django.conf import settings
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth import authenticate, login
from django.contrib.auth import views as auth_views

from django.db.models import Count

from foodcartapp.models import Product, Restaurant, Order, OrderProduct
from foodcartapp.models import RestaurantMenuItem
from geoapp.models import Place

class Login(forms.Form):
    username = forms.CharField(
        label='Логин', max_length=75, required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Укажите имя пользователя'
        })
    )
    password = forms.CharField(
        label='Пароль', max_length=75, required=True,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Введите пароль'
        })
    )


class LoginView(View):
    def get(self, request, *args, **kwargs):
        form = Login()
        return render(request, "login.html", context={
            'form': form
        })

    def post(self, request):
        form = Login(request.POST)

        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']

            user = authenticate(request, username=username, password=password)
            if user:
                login(request, user)
                if user.is_staff:  # FIXME replace with specific permission
                    return redirect("restaurateur:RestaurantView")
                return redirect("start_page")

        return render(request, "login.html", context={
            'form': form,
            'ivalid': True,
        })


class LogoutView(auth_views.LogoutView):
    next_page = reverse_lazy('restaurateur:login')


def is_manager(user):
    return user.is_staff  # FIXME replace with specific permission


@user_passes_test(is_manager, login_url='restaurateur:login')
def view_products(request):
    restaurants = list(Restaurant.objects.order_by('name'))
    products = list(Product.objects.prefetch_related('menu_items'))

    products_with_restaurant_availability = []
    for product in products:
        availability = {item.restaurant_id: item.availability for item in product.menu_items.all()}
        ordered_availability = [availability.get(restaurant.id, False) for restaurant in restaurants]

        products_with_restaurant_availability.append(
            (product, ordered_availability)
        )

    return render(request, template_name="products_list.html", context={
        'products_with_restaurant_availability': products_with_restaurant_availability,
        'restaurants': restaurants,
    })


@user_passes_test(is_manager, login_url='restaurateur:login')
def view_restaurants(request):
    return render(request, template_name="restaurants_list.html", context={
        'restaurants': Restaurant.objects.all(),
    })


def fetch_coordinates(address):
    base_url = "https://geocode-maps.yandex.ru/1.x"
    response = requests.get(base_url, params={
        "geocode": address,
        "apikey": settings.YANDEX_API_KEY,
        "format": "json",
    })
    response.raise_for_status()
    found_places = response.json()['response']['GeoObjectCollection']['featureMember']

    if not found_places:
        return None

    most_relevant = found_places[0]
    lon, lat = most_relevant['GeoObject']['Point']['pos'].split(" ")
    return lat, lon


def get_place_coordinates(places, address):
    place = [place for place in places if place.address == address]
    if not place:
        coords = fetch_coordinates(address)
        if not coords:
            return None
        lat, lon = coords
        place = Place.objects.create(
            address=address,
            lat=lat,
            lon=lon,
            request_date=timezone.now(),
        )
    else:
        place = place[0]
    return place.lat, place.lon


def get_restaurants_details(order, menu_items, restaurants, places):
    if order.restaurant:
        return (f'Готовит {order.restaurant.name}', None)

    order_products = (order.order_products.all().values_list('product'))
    order_restaurants = (
        menu_items
        .filter(product__in=order_products)
        .values('restaurant')
        .annotate(products_count=Count('product'))
        .filter(products_count=order_products.count())
        .values('restaurant')
    )

    if order_restaurants:
        order_coords = get_place_coordinates(places, order.address)
        if not order_coords:
            return ('Ошибка определения координат', None)

        available_restaurants = []
        for restaurant in restaurants:
            if {'restaurant': restaurant.pk} in order_restaurants:
                restaurant_coords = get_place_coordinates(places, restaurant.address)
                if not restaurant_coords:
                    return ('Ошибка определения координат', None)
                order_distance = '{:.2f}'.format(
                    distance.distance(order_coords, restaurant_coords).km
                )
                available_restaurants.append({restaurant: order_distance})
        return ('Может быть приготовлен ресторанами:', available_restaurants)

    return ('Нет ресторана со всеми позициями', None)


@user_passes_test(is_manager, login_url='restaurateur:login')
def view_orders(request):
    orders = (
        Order.objects
        .select_related('restaurant')
        .prefetch_related('order_products')
        .order_with_price()
        .exclude(status='3')
        .order_by('restaurant', 'registered_at')
    )
    menu_items = RestaurantMenuItem.objects.select_related('restaurant')\
                                           .select_related('product')
    restaurants = list(Restaurant.objects.all())
    places = list(Place.objects.all())

    orders_with_restaurants = []
    for order in orders:
        summary, available_restaurants = get_restaurants_details(
            order,
            menu_items,
            restaurants,
            places,
        )
        orders_with_restaurants.append((order, summary, available_restaurants))
    return render(request, template_name='order_items.html', context={
        'orders_with_restaurants': orders_with_restaurants,
    })
