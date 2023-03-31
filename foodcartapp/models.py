from geopy import distance

from django.db import models
from django.core.validators import MinValueValidator
from phonenumber_field.modelfields import PhoneNumberField
from django.db.models import F, Sum, Count
from django.utils import timezone
from geoapp.geocoding import get_place_coordinates


class Restaurant(models.Model):
    name = models.CharField(
        'название',
        max_length=50
    )
    address = models.CharField(
        'адрес',
        max_length=100,
        blank=True,
    )
    contact_phone = models.CharField(
        'контактный телефон',
        max_length=50,
        blank=True,
    )

    class Meta:
        verbose_name = 'ресторан'
        verbose_name_plural = 'рестораны'

    def __str__(self):
        return self.name


class ProductQuerySet(models.QuerySet):
    def available(self):
        products = (
            RestaurantMenuItem.objects
            .filter(availability=True)
            .values_list('product')
        )
        return self.filter(pk__in=products)


class ProductCategory(models.Model):
    name = models.CharField(
        'название',
        max_length=50
    )

    class Meta:
        verbose_name = 'категория'
        verbose_name_plural = 'категории'

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(
        'название',
        max_length=50
    )
    category = models.ForeignKey(
        ProductCategory,
        verbose_name='категория',
        related_name='products',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    price = models.DecimalField(
        'цена',
        max_digits=8,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    image = models.ImageField(
        'картинка'
    )
    special_status = models.BooleanField(
        'спец.предложение',
        default=False,
        db_index=True,
    )
    description = models.TextField(
        'описание',
        max_length=200,
        blank=True,
    )

    objects = ProductQuerySet.as_manager()

    class Meta:
        verbose_name = 'товар'
        verbose_name_plural = 'товары'

    def __str__(self):
        return self.name


class RestaurantMenuItem(models.Model):
    restaurant = models.ForeignKey(
        Restaurant,
        related_name='menu_items',
        verbose_name="ресторан",
        on_delete=models.CASCADE,
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='menu_items',
        verbose_name='продукт',
    )
    availability = models.BooleanField(
        'в продаже',
        default=True,
        db_index=True
    )

    class Meta:
        verbose_name = 'пункт меню ресторана'
        verbose_name_plural = 'пункты меню ресторана'
        unique_together = [
            ['restaurant', 'product']
        ]

    def __str__(self):
        return f"{self.restaurant.name} - {self.product.name}"


class OrderQuerySet(models.QuerySet):

    def order_with_price(self):
        order_with_full_price = self.annotate(
            full_price=Sum(F('order_products__price'))
        )\
        .order_by('id')
        return order_with_full_price

    def get_orders(self):
        orders = (
            Order.objects
            .select_related('restaurant')
            .prefetch_related('order_products')
            .order_with_price()
            .exclude(status='3')
            .order_by('restaurant', 'registered_at')
        )
        return orders
class Order(models.Model):
    STATUSES = (
        ('new', 'Необработанный'),
        ('cooking', 'Готовится'),
        ('delivering', 'Доставляется'),
        ('completed', 'Выполнен'),
    )

    PAYMENT = (
        ('not_set', 'Не выбран'),
        ('now', 'Сразу'),
        ('online', 'Электронно'),
        ('cash', 'Наличностью'),
    )

    products = models.ManyToManyField(
        Product,
        through='OrderProduct',
        related_name='orders',
    )
    firstname = models.CharField(
        'имя',
        max_length=10
    )
    lastname = models.CharField(
        'фамилия',
        max_length=10
    )
    phonenumber = PhoneNumberField(
        verbose_name='номер телефона',
        region='RU',
        max_length=20,
        db_index=True
    )
    address = models.CharField(
        'адрес',
        max_length=50
    )
    status = models.CharField(
        verbose_name='Статус заказа',
        max_length=20,
        choices=STATUSES,
        default='Необработанный',
        db_index=True
    )
    comment = models.TextField(
        verbose_name='Комментарий к заказу',
        blank=True,
    )
    registered_at = models.DateTimeField(
        verbose_name='Время создания заказа',
        default=timezone.now
    )
    called_at = models.DateTimeField(
        verbose_name='Время звонка',
        db_index=True,
        blank=True,
        null=True
    )
    delivered_at = models.DateTimeField(
        verbose_name='Время доставки',
        db_index=True,
        blank=True,
        null=True
    )
    pay_form = models.CharField(
        verbose_name='Способ оплаты',
        max_length=20,
        choices=PAYMENT,
        default='Не выбран',
        db_index=True
    )
    selected_restaurant = models.ForeignKey(
        Restaurant,
        related_name='orders',
        verbose_name='выбранный ресторан',
        on_delete=models.CASCADE,
        blank=True,
        null=True
    )

    objects = OrderQuerySet.as_manager()

    class Meta:
        verbose_name = 'заказ'
        verbose_name_plural = 'заказы'

    def __str__(self):
        return f'{self.lastname} {self.firstname}'

    def get_restaurants_details(self, order, menu_items, restaurants, places):
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


class OrderProduct(models.Model):
    order = models.ForeignKey(
        'Order',
        verbose_name='Заказ',
        related_name='order_products',
        on_delete=models.CASCADE,
    )
    product = models.ForeignKey(
        'Product',
        verbose_name='Товар',
        on_delete=models.CASCADE,
    )
    quantity = models.IntegerField(
        'Количество',
        validators=[MinValueValidator(1)],
    )
    price = models.DecimalField(
        verbose_name='Цена товара',
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )

    class Meta:
        verbose_name = 'Товар заказа'
        verbose_name_plural = 'Товары заказа'

    def __str__(self):
        return f'{self.product.name} - {self.order.firstname} {self.order.lastname}'
