import time
from datetime import datetime

import schedule
from django.core.management.base import BaseCommand

from food_plan import settings
from foodplan_app.models import Subscription, Recipe, Meal


def check_is_new_year_now():
    return datetime.now().month == 12 and datetime.now().day == 31


def update_subscriptions_recipe(meal):
    subscriptions = (
        Subscription.objects.get_active_subscriptions()
                            .filter(meals__contains=meal)
                            .prefetch_related('excluded_allergens')
    )

    recipes = (Recipe.objects.filter(meals__contains=meal)
                             .prefetch_related('items')
                             .prefetch_related('items__product')
                             .prefetch_related('items__product__allergen')
                             .order_by('?'))

    for subscription in subscriptions:
        allergens = subscription.excluded_allergens.values_list(
            'name',
            flat=True
        )

        for recipe in recipes:
            recipe_allergens = [
                item.product.allergen for item in recipe.items.all()
            ]
            if any(allergens) in recipe_allergens:
                continue

            if subscription.menu_type not in recipe.menu_types:
                continue

            subscription.current_recipe = recipe

            break

    Subscription.objects.bulk_update(
        subscriptions,
        fields=('current_recipe',)
    )


class Command(BaseCommand):
    help = 'Run periodic meal change in subscriptions'

    def handle(self, *args, **options):
        schedule.every().day.at(settings.BREAKFAST_TIME).do(
            update_subscriptions_recipe, meal=Meal.BREAKFAST
        )
        schedule.every().day.at(settings.LUNCH_TIME).do(
            update_subscriptions_recipe, meal=Meal.LUNCH
        )
        schedule.every().day.at(settings.DINNER_TIME).do(
            update_subscriptions_recipe, meal=(
                Meal.NEW_YEAR if check_is_new_year_now() else Meal.DINNER
            )
        )
        schedule.every().day.at(settings.DESSERT_TIME).do(
            update_subscriptions_recipe, meal=Meal.DESSERT
        )

        while True:
            schedule.run_pending()
            time.sleep(1)
