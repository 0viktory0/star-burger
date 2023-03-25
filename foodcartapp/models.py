from django.db import models
from django.core.validators import MinValueValidator
from phonenumber_field.modelfields import PhoneNumberField
from django.db.models import Count, F



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

class Order(models.Model):
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

    class Meta:
        verbose_name = 'заказ'
        verbose_name_plural = 'заказы'

    def __str__(self):
        return f'{self.lastname} {self.firstname}'


class OrderProductQuerySet(models.QuerySet):

    def order_price(self):
        order_products = self.annotate(product_price=F('price') * F('quantity'))
        price = 0
        for product in order_products:
            price += product.product_price
        return price


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
        default=1,
        validators=[MinValueValidator(1)],
    )

    objects = OrderProductQuerySet.as_manager()

    price = models.DecimalField(
        verbose_name='Цена товара',
        max_digits=5,
        decimal_places=2,
        default=1,
        validators=[MinValueValidator(0)]
    )

    class Meta:
        verbose_name = 'Товар заказа'
        verbose_name_plural = 'Товары заказа'

    def __str__(self):
        return f'{self.product.name} - {self.order.firstname} {self.order.lastname}'
