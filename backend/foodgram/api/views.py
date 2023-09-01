from django.db.models import Sum
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

    def subscribed(self, request, pk=None):
        # Пользователь, на которого подписываемся
        author = get_object_or_404(User, pk=pk)
        # Текущий пользователь
        user = request.user
        if user == author:
            return Response({"message": "Нельзя подписаться на самого себя!"},
                            status=status.HTTP_400_BAD_REQUEST)
        Subscription.objects.get_or_create(user=user, author=author)
        serializer = SubscriptionSerializer(
            author, context={'request': request})
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def unsubscribed(self, request, pk):
        author = get_object_or_404(User, pk=pk)
        user = request.user
        Subscription.objects.filter(user=user, author=author).delete()
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
            if Favorite.objects.filter(user=user, recipe=recipe).exists():
                return Response({"message": "Рецепт уже добавлен в избранное"},
                                status=status.HTTP_400_BAD_REQUEST)
            Favorite.objects.create(user=user, recipe=recipe)
            serializer = FavorShopRecipeSerializer(recipe)
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
            if ShoppingList.objects.filter(user=user, recipe=recipe).exists():
                return Response(
                    {"message": "Рецепт уже добавлен в список покупок"},
                    status=status.HTTP_400_BAD_REQUEST)
            ShoppingList.objects.create(user=user, recipe=recipe)
            serializer = FavorShopRecipeSerializer(recipe)
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
        shopping_cart = ShoppingList.objects.filter(user=request.user)
        recipes_id = [item.recipe.id for item in shopping_cart]
        ingredients = RecipeIngredient.objects.filter(
            recipe__in=recipes_id).values(
            "ingredient__name", "ingredient__measurement_unit").annotate(
            amount=Sum("amount"))
        final_list = self.create_shopping_list(ingredients)
        file_name = "shopping_list.txt"
        response = HttpResponse(final_list, content_type="text/plain")
        response["Content-Disposition"] = f"attachment; filename={file_name}"
        return response

    def create_shopping_list(self, ingredients):
        shopping_list = ["Список покупок", ""]
        for item in ingredients:
            ingredient_name = item["ingredient__name"]
            measurement_unit = item["ingredient__measurement_unit"]
            amount = item["amount"]
            shopping_list.append(
                f'{ingredient_name} ({measurement_unit}) {amount}')
        return "\n".join(shopping_list)
