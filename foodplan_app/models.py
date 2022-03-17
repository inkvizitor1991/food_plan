from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from django.db import models
from multiselectfield import MultiSelectField


class MenuType(models.TextChoices):
    CLASSIC = 'classic', 'классическое'
    LOW_CARB = 'low_carb', 'низкоуглеводное'
    VEGETARIAN = 'vegetarian', 'вегетарианское'
    KETO = 'keto', 'кето'


class Meal(models.TextChoices):
    BREAKFAST = 'breakfast', 'завтрак'
    LUNCH = 'lunch', 'обед'
    DINNER = 'dinner', 'ужин'
    DESSERT = 'dessert', 'десерт'
    NEW_YEAR = 'new_year', 'новогодний'


class Allergen(models.Model):
    name = models.CharField(
        max_length=100,
        unique=True,
        verbose_name='название'
    )

    class Meta:
        verbose_name = 'аллерген'
        verbose_name_plural = 'аллергены'


class Product(models.Model):
    name = models.CharField(
        max_length=100,
        unique=True,
        verbose_name='название'
    )

    allergen = models.ForeignKey(
        Allergen,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        default=None
    )

    class Meta:
        verbose_name = 'продукт'
        verbose_name_plural = 'продукты'


class Receipt(models.Model):
    name = models.CharField(
        max_length=100,
        unique=True,
        verbose_name='название'
    )

    description = models.TextField(
        blank=True,
        verbose_name='описание'
    )
    image = models.ImageField(
        blank=True,
        verbose_name='изображение'
    )

    meal = models.CharField(
        max_length=50,
        verbose_name='прием пищи',
        choices=Meal.choices
    )

    menu_type = models.CharField(
        max_length=50,
        verbose_name='тип меню',
        choices=MenuType.choices
    )

    class Meta:
        verbose_name = 'рецепт'
        verbose_name_plural = 'рецепты'


class ReceiptItem(models.Model):
    receipt = models.ForeignKey(
        Receipt,
        on_delete=models.CASCADE,
        related_name='items'
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='receipts_items'
    )

    quantity = models.CharField(
        max_length=50,
        verbose_name='количество'
    )
    price = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        verbose_name='цена',
        validators=[MinValueValidator(0)]
    )

    class Meta:
        verbose_name = 'элемент рецепта'
        verbose_name_plural = 'элементы рецепта'


class Subscription(models.Model):
    class MonthCount(models.IntegerChoices):
        YEAR = 12, 'год'
        THREE_MONTH = 3, 'три месяца'

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )

    persons_count = models.IntegerField(
        verbose_name='количество персон',
        validators=[MinValueValidator(1)]
    )

    excluded_allergens = models.ManyToManyField(
        Allergen,
        related_name='excluded_subscriptions',
        verbose_name='исключенные аллергены',
        blank=True
    )

    months_count = models.IntegerField(
        verbose_name='количество месяцев подписки',
        choices=MonthCount.choices
    )
    last_payed_at = models.DateField(
        verbose_name='дата последней оплаты'
    )

    current_receipt = models.ForeignKey(
        Receipt,
        verbose_name='текущий рецепт',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        default=None
    )

    meals = MultiSelectField(
        choices=Meal.choices,
        blank=True,
        default=tuple()
    )

    class Meta:
        verbose_name = 'подписка'
        verbose_name_plural = 'подписки'
