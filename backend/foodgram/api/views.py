from collections import defaultdict

from django.db.models import Sum
from django.db.models.functions import Coalesce
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from recipes.models import (Favorite, Ingredient, Recipe, RecipeIngredient,
                            ShoppingList, Tag)
from users.models import Subscription, User
from .filters import IngredientSearch, RecipeFilter
from .mixins import SimpleViewSet
from .pagination import FoodgramPagination
from .permissions import IsAuthorOrReadOnly
from .serializers import (CreateRecipeSerializer, FavorShopRecipeSerializer,
                          IngredientSerializer, ReadRecipeSerializer,
                          SubscriptionSerializer, TagSerializer,
                          UserProfileSerializer)


class UserViewSet(viewsets.ModelViewSet):
    """Вьюсет для модели пользователя."""
    queryset = User.objects.all()
    serializer_class = UserProfileSerializer
    permission_classes = (AllowAny,)
    pagination_class = FoodgramPagination

    def subscribed(self, request, pk):
        author = get_object_or_404(User, pk=pk)
        serializer = SubscriptionSerializer(
            author, context={"request": request})
        serializer.validate(serializer.data)
        Subscription.objects.get_or_create(user=request.user, author=author)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def unsubscribed(self, request, pk):
        author = get_object_or_404(User, pk=pk)
        request.user.follower.filter(author=author).delete()
        return Response({"message": "Вы отписались от автора рецепта!"},
                        status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=True,
        methods=["post", "delete"],
        permission_classes=[IsAuthenticated],
    )
    def subscribe(self, request, pk):
        if request.method == "DELETE":
            return self.unsubscribed(request, pk)
        return self.subscribed(request, pk)

    @action(
        detail=False,
        methods=["get"],
        permission_classes=[IsAuthenticated]
    )
    def subscriptions(self, request):
        queryset = User.objects.filter(following__user=request.user)
        paginator = self.pagination_class()
        paginated_queryset = paginator.paginate_queryset(queryset, request)
        serializer = SubscriptionSerializer(
            paginated_queryset, many=True, context={"request": request})
        return paginator.get_paginated_response(serializer.data)


class TagViewSet(SimpleViewSet):
    """Вьюсет для тега."""
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class IngredientViewSet(SimpleViewSet):
    """Вьюсет для игредиента."""
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = (IngredientSearch,)
    search_fields = ("^name",)


class RecipeViewSet(viewsets.ModelViewSet):
    """Вьюсет для рецепта."""
    queryset = Recipe.objects.all()
    permission_classes = (IsAuthorOrReadOnly,)
    pagination_class = FoodgramPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter
    http_method_names = ["get", "post", "patch", "delete"]

    def get_serializer_class(self):
        if self.request.method == "POST" or self.request.method == "PATCH":
            return CreateRecipeSerializer
        return ReadRecipeSerializer

    @action(
        detail=True,
        methods=["post", "delete"],
        permission_classes=[IsAuthenticated]
    )
    def favorite(self, request, pk):
        recipe = get_object_or_404(Recipe, pk=pk)
        user = request.user
        if request.method == "POST":
            serializer = FavorShopRecipeSerializer(
                recipe, context={"request": request})
            serializer.validate_favorited(serializer.data)
            Favorite.objects.create(user=user, recipe=recipe)
            return Response(data=serializer.data,
                            status=status.HTTP_201_CREATED)
        deleted = get_object_or_404(Favorite, user=user, recipe=recipe)
        deleted.delete()
        return Response({"message": "Рецепт удален из избранного"},
                        status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=True,
        methods=["post", "delete"],
        permission_classes=[IsAuthenticated]
    )
    def shopping_cart(self, request, pk):
        recipe = get_object_or_404(Recipe, pk=pk)
        user = request.user
        if request.method == "POST":
            serializer = FavorShopRecipeSerializer(
                recipe, context={"request": request})
            serializer.validate_shopping_cart(serializer.data)
            ShoppingList.objects.create(user=user, recipe=recipe)
            return Response(data=serializer.data,
                            status=status.HTTP_201_CREATED)
        deleted = get_object_or_404(ShoppingList, user=user, recipe=recipe)
        deleted.delete()
        return Response({"message": "Рецепт удален из списка покупок"},
                        status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False,
        methods=["get"],
        permission_classes=[IsAuthenticated]
    )
    def download_shopping_cart(self, request):
        shopping_cart = request.user.shopping_lists.all()
        ingredients_data = RecipeIngredient.objects.filter(
            recipe__in=[item.recipe for item in shopping_cart]
        ).values(
            "ingredient__name",
            "ingredient__measurement_unit"
        ).annotate(
            amount=Coalesce(Sum("amount"), 0)
        )

        final_list = defaultdict(lambda: {"measurement_unit": "", "amount": 0})
        for item in ingredients_data:
            ingredient_name = item["ingredient__name"]
            measurement_unit = item["ingredient__measurement_unit"]
            amount = item["amount"]
            final_list[ingredient_name]["measurement_unit"] = measurement_unit
            final_list[ingredient_name]["amount"] += amount

        shopping_list = ["Список покупок", ""]
        for key, value in final_list.items():
            shopping_list.append(
                f"{key} - {value['amount']} {value['measurement_unit']}")
        shopping_list_text = "\n".join(shopping_list)
        response = HttpResponse(shopping_list_text, content_type="text/plain")
        return response
