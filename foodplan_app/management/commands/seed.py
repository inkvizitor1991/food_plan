from urllib.parse import urlparse

import requests
from django.conf import settings
from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand

from foodplan_app.models import MenuType, Meal, Recipe, Product, RecipeItem


RECIPE_API_URL = 'https://api.edamam.com/api/recipes/v2?type=public'

DEFAULT_DIET = MenuType.CLASSIC

MEAL_TYPES = {
    'lunch': Meal.LUNCH,
    'dinner': Meal.DINNER,
    'breakfast': Meal.BREAKFAST,
    'brunch': Meal.DESSERT
}


class Command(BaseCommand):
    help = 'Seed recipes data'

    def add_arguments(self, parser):
        parser.add_argument('--pages')
        parser.add_argument('--search')

    def handle(self, *args, **options):
        app_id = settings.EDAMAM_APP_ID
        app_key = settings.EDAMAM_APP_KEY
        next_link = RECIPE_API_URL
        recipes_to_create = []
        recipes_items_to_create = []

        pages = options['pages']
        if not pages:
            pages = 1
        search = options['search']
        if not search:
            search = ''

        existed_recipe_names = list(Recipe.objects.all().values_list(
            'name',
            flat=True
        ))

        existed_products = {
            product.name: product
            for product in Product.objects.all()
        }

        for _ in range(pages):
            response = requests.get(
                url=next_link,
                params={
                    'q': search,
                    'app_id': app_id,
                    'app_key': app_key,
                    'imageSize': 'LARGE'
                }
            )
            response.raise_for_status()

            api_answer = response.json()

            next_link = api_answer['_links']['next']['href']

            recipes = [hit['recipe'] for hit in api_answer['hits']]

            for recipe in recipes:
                title = recipe['label']

                if title in existed_recipe_names:
                    continue
                else:
                    existed_recipe_names.append(title)

                diet_types = []
                meals = []
                diet_labels = recipe['dietLabels']
                health_labels = recipe['healthLabels']

                if 'Low-Carb' in diet_labels:
                    diet_types.append(MenuType.LOW_CARB)
                if 'Keto-Friendly' in health_labels:
                    diet_types.append(MenuType.KETO)
                if 'Vegeterian' in health_labels:
                    diet_types.append(MenuType.VEGETARIAN)
                if ('Balanced' in diet_labels) or (not diet_types):
                    diet_types.append(MenuType.CLASSIC)

                for meal in MEAL_TYPES:
                    if meal in recipe['mealType'][0]:
                        meals.append(meal)

                description = recipe['url']
                image_url = recipe['images']['LARGE']['url']

                image_name = urlparse(image_url).path.split('/')[-1]
                image_response = requests.get(image_url)
                image_response.raise_for_status()

                recipe_to_create = Recipe(
                    name=title,
                    description=description,
                    meals=meals,
                    menu_types=diet_types
                )

                recipe_to_create.image.save(
                    image_name,
                    ContentFile(image_response.content)
                )

                recipes_to_create.append(recipe_to_create)

                for ingredient in recipe['ingredients']:
                    product_name = ingredient['food']
                    if product_name in existed_products:
                        product = existed_products[product_name]
                    else:
                        product = Product.objects.create(
                            name=product_name
                        )
                        existed_products[product.name] = product

                    quantity = (f"{ingredient['quantity']} "
                                f"{ingredient['measure']}")

                    recipe_item = RecipeItem(
                        recipe=recipe_to_create,
                        product=product,
                        quantity=quantity,
                        price=0
                    )

                    recipes_items_to_create.append(recipe_item)

        Recipe.objects.bulk_create(
            recipes_to_create,
            ignore_conflicts=True
        )
        RecipeItem.objects.bulk_create(
            recipes_items_to_create,
            ignore_conflicts=True
        )

