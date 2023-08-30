from django_filters.rest_framework import FilterSet, filters
from recipes.models import Recipe, Tag, User

CHOICES = (
    ("0", "False"),
    ("1", "True")
)


class RecipeFilter(FilterSet):
    """Фильтр для рецептов."""
    is_favorited = filters.ChoiceFilter(
        choices=CHOICES,
        method="get_is_favorited",
    )
    is_in_shopping_cart = filters.ChoiceFilter(
        choices=CHOICES,
        method="get_is_in_shopping_cart",
    )
    author = filters.ModelChoiceFilter(
        queryset=User.objects.all()
    )

    tags = filters.ModelChoiceFilter(
        field_name="tags__slug",
        to_field_name="slug",
        queryset=Tag.objects.all()
    )

    def get_is_favorited(self, queryset, name, value):
        user = self.request.user
        if value in CHOICES and user.is_authenticated:
            return queryset.filter(favorites__user=user)
        return queryset

    def get_is_in_shopping_cart(self, queryset, name, value):
        user = self.request.user
        if value in CHOICES and user.is_authenticated:
            return queryset.filter(shopping_lists__user=user)
        return queryset

    class Meta:
        model = Recipe
        fields = ("is_favorited", "is_in_shopping_cart", "author", "tags")
