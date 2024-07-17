from django.contrib import admin

from .models import (
    Ingredient,
    RecipeIngredient,
    Recipe,
    Tag,
    Favorite
)


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'measurement_unit',
    )
    search_fields = ('name',)
    list_filter = ('measurement_unit',)
    list_display_links = ('name',)
    empty_value_display = 'Не задано'


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'slug',
    )
    search_fields = ('name',)
    list_display_links = ('name',)
    empty_value_display = 'Не задано'


class RecipeIngredientInline(admin.TabularInline):
    model = RecipeIngredient
    extra = 2


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'author',
        'pub_date',
        'number_to_favorites'
    )
    search_fields = (
        'name',
        'author'
    )
    filter_horizontal = ('tags',)
    list_display_links = ('name',)
    empty_value_display = 'Не задано'
    inlines = (RecipeIngredientInline,)

    @admin.display(description="Добавлено в избранное")
    def number_to_favorites(self, obj):
        return Favorite.objects.filter(recipe=obj).count()


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'recipe'
    )
    search_fields = (
        'user',
        'recipe'
    )
