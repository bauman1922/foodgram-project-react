import webcolors
from djoser.serializers import UserCreateSerializer, UserSerializer
from drf_extra_fields.fields import Base64ImageField
from recipes.models import (Favorite, Ingredient, Recipe, RecipeIngredient,
                            ShoppingList, Tag)
from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from users.models import Subscription, User


class UserRegistrationSerializer(UserCreateSerializer):
    """Сериализатор создания пользователя."""
    email = serializers.EmailField(
        validators=[UniqueValidator(queryset=User.objects.all())]
    )
    password = serializers.CharField(
        write_only=True,
    )
    username = serializers.CharField(
        validators=[UniqueValidator(queryset=User.objects.all())])

    class Meta:
        model = User
        fields = (
            "id",
            "email",
            "username",
            "first_name",
            "last_name",
            "password",
        )


class UserProfileSerializer(UserSerializer):
    """Сериализатор профиля пользователя."""
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            "email",
            "id",
            "username",
            "first_name",
            "last_name",
            "is_subscribed"
        )

    def get_is_subscribed(self, obj):
        current_user = self.context.get("request").user
        if not current_user.is_authenticated:
            return False
        return Subscription.objects.filter(
            user=current_user, author=obj).exists()


class Hex2NameColor(serializers.Field):
    """Класс для преобразования шестнадцатеричного кода цвета в его имя."""
    def to_representation(self, value):
        return value

    def to_internal_value(self, data):
        try:
            data = webcolors.hex_to_name(data)
        except ValueError:
            raise serializers.ValidationError("Для этого цвета нет имени")
        return data


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор тэга."""
    color = Hex2NameColor()

    class Meta:
        model = Tag
        fields = "__all__"


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор ингредиента."""
    class Meta:
        model = Ingredient
        fields = "__all__"


class ReadRecipeIngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для чтения ингредиентов в рецепте."""
    id = serializers.ReadOnlyField(
        source="ingredient.id",
    )
    name = serializers.ReadOnlyField(
        source="ingredient.name",
    )
    measurement_unit = serializers.ReadOnlyField(
        source="ingredient.measurement_unit",
    )

    class Meta:
        model = RecipeIngredient
        fields = ("id", "name", "measurement_unit", "amount")


class ReadRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для чтения рецепта."""
    tags = TagSerializer(read_only=True, many=True)
    author = UserProfileSerializer(read_only=True)
    ingredients = serializers.SerializerMethodField()
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            "id",
            "tags",
            "author",
            "ingredients",
            "is_favorited",
            "is_in_shopping_cart",
            "name",
            "image",
            "text",
            "cooking_time",
        )

    def get_ingredients(self, obj):
        ingredients = RecipeIngredient.objects.filter(recipe=obj)
        return ReadRecipeIngredientSerializer(ingredients, many=True).data

    def get_is_favorited(self, obj):
        request = self.context.get("request")
        if request is None or request.user.is_anonymous:
            return False
        return Favorite.objects.filter(recipe=obj, user=request.user).exists()

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get("request")
        if request is None or request.user.is_anonymous:
            return False
        return ShoppingList.objects.filter(
            recipe=obj, user=request.user).exists()


class CreateRecipeIngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для создания ингредиентов в рецепте."""
    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all()
    )
    amount = serializers.IntegerField(write_only=True)

    class Meta:
        model = RecipeIngredient
        fields = ("id", "amount")


class CreateRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для создания рецепта."""
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True
    )
    author = UserProfileSerializer(read_only=True)
    image = Base64ImageField()
    ingredients = CreateRecipeIngredientSerializer(many=True)
    cooking_time = serializers.IntegerField()

    class Meta:
        model = Recipe
        fields = (
            "id",
            "tags",
            "author",
            "ingredients",
            "name",
            "image",
            "text",
            "cooking_time",
        )

    def create(self, validated_data):
        ingredients = validated_data.pop("ingredients")
        tags = validated_data.pop("tags")
        author = self.context.get("request").user
        recipe = Recipe.objects.create(author=author, **validated_data)
        for ingredient in ingredients:
            current_ingredient = ingredient["id"]
            amount = ingredient["amount"]
            RecipeIngredient.objects.create(
                ingredient=current_ingredient, recipe=recipe, amount=amount)
        recipe.tags.set(tags)
        return recipe

    def update(self, instance, validated_data):
        ingredients_data = validated_data.pop("ingredients")
        tags = validated_data.pop("tags")

        instance.name = validated_data.get("name", instance.name)
        instance.image = validated_data.get("image", instance.image)
        instance.text = validated_data.get("text", instance.text)
        instance.cooking_time = validated_data.get("cooking_time", instance.cooking_time)

        instance.tags.set(tags)

        instance.ingredients.all().delete()
        for ingredient_data in ingredients_data:
            ingredient_id = ingredient_data["id"]
            amount = ingredient_data["amount"]
            RecipeIngredient.objects.create(
                ingredient_id=ingredient_id, recipe=instance, amount=amount)
        instance.save()
        return instance
