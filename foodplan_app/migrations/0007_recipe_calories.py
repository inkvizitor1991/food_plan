# Generated by Django 4.0.3 on 2022-03-18 08:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('foodplan_app', '0006_recipe_source_alter_product_allergen_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='recipe',
            name='calories',
            field=models.PositiveIntegerField(blank=True, default=0, verbose_name='калории'),
        ),
    ]