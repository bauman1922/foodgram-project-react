import webcolors
from djoser.serializers import UserCreateSerializer, UserSerializer
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers
from rest_framework.validators import UniqueValidator, ValidationError

from recipes.models import Ingredient, Recipe, RecipeIngredient, Tag, Favorite, ShoppingList
from users.models import Subscription, User

MIN_COUNT = 1
MAX_COUNT = 32000


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
        return (
            current_user.follower.filter(author=obj).exists()
            if current_user.is_authenticated
            else False
        )


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
        ingredients = obj.recipe_ingredients.all()
        return ReadRecipeIngredientSerializer(ingredients, many=True).data

    def get_is_favorited(self, obj):
        current_user = self.context.get("request").user
        return (
            current_user.favorites.filter(recipe=obj).exists()
            if current_user.is_authenticated
            else False
        )

    def get_is_in_shopping_cart(self, obj):
        current_user = self.context.get("request").user
        return (
            current_user.shopping_lists.filter(recipe=obj).exists()
            if current_user.is_authenticated
            else False
        )


class CreateRecipeIngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для создания ингредиентов в рецепте."""
    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all()
    )
    amount = serializers.IntegerField(
        write_only=True, max_value=MAX_COUNT, min_value=MIN_COUNT)

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
    cooking_time = serializers.IntegerField(
        max_value=MAX_COUNT, min_value=MIN_COUNT)

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

    def create_ingredients(self, recipe, ingredients):
        recipe_ingredients = []
        for ingredient in ingredients:
            current_ingredient = ingredient["id"]
            amount = ingredient["amount"]
            recipe_ingredients.append(
                RecipeIngredient(
                    ingredient=current_ingredient,
                    recipe=recipe,
                    amount=amount
                )
            )
        RecipeIngredient.objects.bulk_create(recipe_ingredients)

    def create(self, validated_data):
        ingredients = validated_data.pop("ingredients")
        tags = validated_data.pop("tags")
        author = self.context.get("request").user
        recipe = Recipe.objects.create(author=author, **validated_data)
        self.create_ingredients(recipe, ingredients)
        recipe.tags.set(tags)
        return recipe

    def update(self, instance, validated_data):
        ingredients = validated_data.pop("ingredients")
        tags = validated_data.pop("tags")
        instance.name = validated_data.get("name", instance.name)
        instance.image = validated_data.get("image", instance.image)
        instance.text = validated_data.get("text", instance.text)
        instance.cooking_time = validated_data.get(
            "cooking_time", instance.cooking_time)
        instance.tags.set(tags)
        instance.ingredients.all().delete()
        self.create_ingredients(instance, ingredients)
        instance.save()
        return instance

    def to_representation(self, instance):
        return ReadRecipeSerializer(instance, context={
            "request": self.context.get("request")
        }).data


class FavorShopRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для добавления рецепта в избранное и список покупок."""
    class Meta:
        model = Recipe
        fields = (
            "id",
            "name",
            "image",
            "cooking_time",
        )

    def validate_favorited(self, data):
        current_user = self.context.get("request").user
        if Favorite.objects.filter(user=current_user, recipe=data["id"]
                                   ).exists():
            raise ValidationError("Рецепт уже добавлен в избранное!")
        return data

    def validate_shopping_cart(self, data):
        current_user = self.context.get("request").user
        if ShoppingList.objects.filter(user=current_user, recipe=data["id"]
                                       ).exists():
            raise ValidationError("Рецепт уже добавлен в список покупок!")
        return data


class SubscriptionSerializer(serializers.ModelSerializer):
    """Сериализатор для подписок."""
    recipes_count = serializers.SerializerMethodField(read_only=True)
    is_subscribed = serializers.SerializerMethodField(read_only=True)
    recipes = FavorShopRecipeSerializer(many=True, read_only=True)

    class Meta:
        model = User
        fields = (
            "email",
            "id",
            "username",
            "first_name",
            "last_name",
            "is_subscribed",
            "recipes",
            "recipes_count",
        )

    def get_recipes_count(self, obj):
        return obj.recipes.all().count()

    def get_is_subscribed(self, obj):
        current_user = self.context.get("request").user
        return (
            current_user.follower.filter(author=obj).exists()
            if current_user.is_authenticated
            else False
        )

    def validate(self, data):
        current_user = self.context.get("request").user
        if Subscription.objects.filter(user=current_user, author=data["id"]
                                       ).exists():
            raise ValidationError("Вы уже подписаны на этого пользователя!")
        if self.context.get("request").user.id == data["id"]:
            raise ValidationError("Нельзя подписаться на самого себя!")
        return data
