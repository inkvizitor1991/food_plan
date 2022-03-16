from django.contrib import admin

from .models import (Allergen,
                     Product,
                     Receipt,
                     ReceiptItem,
                     Subscription)


@admin.register(Allergen)
class AllergenAdmin(admin.ModelAdmin):
    pass


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    pass


class ReceiptItemInline(admin.TabularInline):
    model = ReceiptItem
    raw_id_fields = ('product',)


@admin.register(Receipt)
class ReceiptAdmin(admin.ModelAdmin):
    inlines = (ReceiptItemInline,)


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    raw_id_fields = ('user',)
    pass
