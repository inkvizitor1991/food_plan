from datetime import timedelta

from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import Q
from django.utils import timezone
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
        default=None,
        verbose_name='аллерген'
    )

    class Meta:
        verbose_name = 'продукт'
        verbose_name_plural = 'продукты'

    def __str__(self):
        return self.name


class Recipe(models.Model):
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
    source = models.URLField(
        blank=True,
        verbose_name='Источник'
    )

    meals = MultiSelectField(
        verbose_name='приемы пищи',
        choices=Meal.choices,
        default=tuple(),
        blank=True
    )

    menu_types = MultiSelectField(
        verbose_name='типы меню',
        choices=MenuType.choices,
        default=tuple(),
        blank=True
    )

    calories = models.PositiveIntegerField(
        verbose_name='калории',
        blank=True,
        default=0
    )

    class Meta:
        verbose_name = 'рецепт'
        verbose_name_plural = 'рецепты'

    def __str__(self):
        return self.name


class RecipeItem(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name='рецепт'
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='receipts_items',
        verbose_name='продукт'
    )

    quantity = models.PositiveIntegerField(
        verbose_name='Количество'
    )

    measure = models.CharField(
        max_length=50,
        verbose_name='Единица измерения'
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


class SubscriptionQuerySet(models.QuerySet):
    def get_active_subscriptions(self):
        now = timezone.now()
        before_three_months = (now - timedelta(days=90)).date()
        before_twelve_months = (now - timedelta(days=360)).date()

        return self.filter(
            (
                Q(months_count=Subscription.MonthCount.THREE_MONTH)
                & Q(last_payed_at__gte=before_three_months)
            )
            | (
                Q(months_count=Subscription.MonthCount.YEAR)
                & Q(last_payed_at__gte=before_twelve_months)
            )
        )


class Subscription(models.Model):
    class MonthCount(models.IntegerChoices):
        YEAR = 12, 'год'
        THREE_MONTH = 3, 'три месяца'

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='пользователь'
    )

    menu_type = models.CharField(
        max_length=50,
        verbose_name='Тип меню',
        choices=MenuType.choices
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

    current_recipe = models.ForeignKey(
        Recipe,
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

    objects = SubscriptionQuerySet.as_manager()

    class Meta:
        verbose_name = 'подписка'
        verbose_name_plural = 'подписки'
