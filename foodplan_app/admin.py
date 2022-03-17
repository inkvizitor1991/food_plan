from django.contrib import admin

from .models import (Allergen,
                     Product,
                     Recipe,
                     RecipeItem,
                     Subscription)


@admin.register(Allergen)
class AllergenAdmin(admin.ModelAdmin):
    pass


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    pass


class RecipeItemInline(admin.TabularInline):
    model = RecipeItem
    raw_id_fields = ('product',)


@admin.register(Recipe)
class ReceiptAdmin(admin.ModelAdmin):
    inlines = (RecipeItemInline,)


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    raw_id_fields = ('user',)
    pass
