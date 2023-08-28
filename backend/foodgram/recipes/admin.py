from django.contrib import admin

from .models import (Favorite, Ingredient, Recipe, RecipeIngredient,
                     ShoppingList, Tag)


class TagAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "color", "slug")
    search_fields = ("name",)
    list_filter = ("slug",)
    empty_value_display = "-пусто-"


class IngredientAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "measurement_unit")
    search_fields = ("name",)
    list_filter = ("name",)
    empty_value_display = "-пусто-"


class RecipeAdmin(admin.ModelAdmin):
    list_display = ("id", "author", "name", "favorites_count_display")
    search_fields = ("name",)
    list_filter = ("author__username", "name", 'tags__name')
    empty_value_display = "-пусто-"

    def favorites_count_display(self, obj):
        favorites_count = Favorite.objects.filter(recipe=obj).count()
        return favorites_count

    favorites_count_display.short_description = "В избранном"


class RecipeIngredientAdmin(admin.ModelAdmin):
    list_display = ("id", "recipe", "ingredient", "amount")
    empty_value_display = "-пусто-"


class FavoriteAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "recipe")
    search_fields = ("user__username", "recipe__name")
    empty_value_display = "-пусто-"


class ShoppingListAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "recipe")
    search_fields = ("user__username", "recipe__name")
    empty_value_display = "-пусто-"


admin.site.register(Tag, TagAdmin)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(RecipeIngredient, RecipeIngredientAdmin)
admin.site.register(Favorite, FavoriteAdmin)
admin.site.register(ShoppingList, ShoppingListAdmin)
