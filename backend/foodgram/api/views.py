from django.shortcuts import get_object_or_404
from requests import Response
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from recipes.models import Favorite, Ingredient, Recipe, ShoppingList, Tag
from users.models import User

from .serializers import (CreateRecipeSerializer, FavorShopRecipeSerializer,
                          IngredientSerializer, ReadRecipeSerializer,
                          TagSerializer, UserProfileSerializer)


class UserViewSet(viewsets.ModelViewSet):
    """Вьюсет для кастомной модели пользователя."""
    queryset = User.objects.all()
    serializer_class = UserProfileSerializer
    permission_classes = (AllowAny,)


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (AllowAny,)


class IngredientViewSet(viewsets.ModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (AllowAny,)


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    permission_classes = (AllowAny,)

    def get_serializer_class(self):
        if self.request.method == "POST" or self.request.method == "PATCH":
            return CreateRecipeSerializer
        return ReadRecipeSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({"request": self.request})
        return context

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
