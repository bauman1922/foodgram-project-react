from django.contrib import admin

from .models import Ingredient, Recipe, Tag


class TagAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "color", "slug")
    search_fields = ("name",)
    empty_value_diplay = "-пусто-"


class IngredientAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "unit")
    list_filter = ("name",)
    empty_value_diplay = "-пусто-"


class RecipeAdmin(admin.ModelAdmin):
    list_display = ("id", "author", "title")
    search_fields = ("title",)
    list_filter = ("author", "title", 'tags')
    empty_value_diplay = "-пусто-"


admin.site.register(Tag, TagAdmin)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Recipe, RecipeAdmin)
