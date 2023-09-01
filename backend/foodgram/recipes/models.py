from django.core.validators import (MaxValueValidator, MinValueValidator,
                                    RegexValidator)
from django.db import models

from users.models import User

MIN_AMOUNT = 1
MAX_AMOUNT = 32000


class CustomMeta:
    ordering = ("-id",)


class Tag(models.Model):
    name = models.CharField(
        max_length=200,
        unique=True,
        verbose_name="Название тэга",
    )
    color = models.CharField(
        max_length=7,
        unique=True,
        verbose_name="Цвет",
    )
    slug = models.SlugField(
        verbose_name="Slug",
        validators=[
            RegexValidator(
                regex=r"^[-a-zA-Z0-9_]+$",
                message="Slug должен содержать только буквы, цифры, "
                "дефисы и знаки подчеркивания.",
            ),
        ],
    )

    class Meta(CustomMeta):
        verbose_name = "Тэг"
        verbose_name_plural = "Тэги"

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    name = models.CharField(
        max_length=100,
        verbose_name="Название ингредиента",
    )
    measurement_unit = models.CharField(
        max_length=20,
        verbose_name="Единица измерения",
    )

    class Meta(CustomMeta):
        verbose_name = "Ингредиент"
        verbose_name_plural = "Ингредиенты"

    def __str__(self):
        return self.name


class Recipe(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="recipes",
        verbose_name="Автор",
    )
    name = models.CharField(
        max_length=200,
        verbose_name="Назавание рецепта",
    )
    image = models.ImageField(
        upload_to="recipes/",
        verbose_name="Картинка",
    )
    text = models.TextField(
        verbose_name="Описание приготовления",
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through="RecipeIngredient",
        verbose_name="Ингредиент",
    )
    tags = models.ManyToManyField(
        Tag,
        verbose_name="Тэг",
    )
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name="Время приготовления",
        validators=[
            MinValueValidator(MIN_AMOUNT, message="Время приготовления "
                              "должно быть не менее 1 минуты."),
            MaxValueValidator(MAX_AMOUNT, message="Время приготовления "
                              "не может превышать 32000 минут."),
        ]
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата публикации",
        db_index=True,
    )

    class Meta(CustomMeta):
        verbose_name = "Рецепт"
        verbose_name_plural = "Рецепты"

    def __str__(self):
        return self.name


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name="recipe_ingredients",
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name="recipe_ingredients",
    )
    amount = models.PositiveSmallIntegerField(
        verbose_name="Количество ингредиентов",
        validators=[
            MinValueValidator(MIN_AMOUNT, "Количество ингредиентов "
                              "должно быть не менее 1."),
            MaxValueValidator(MAX_AMOUNT, "Количество ингредиентов "
                              "не может превышать 32000."),
        ]
    )

    class Meta(CustomMeta):
        verbose_name = "Рецепт/Ингредиент"
        verbose_name_plural = "Рецепты/Ингредиенты"

    def __str__(self):
        return f"{self.recipe} : {self.ingredient}"


class Favorite(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name="Пользователь",
        related_name="favorites",
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name="Рецепт",
        related_name="favorites",
    )

    class Meta(CustomMeta):
        verbose_name = "Список избранного"
        verbose_name_plural = "Список избранного"

    def __str__(self):
        return f"{self.user} : {self.recipe}"


class ShoppingList(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name="Пользователь",
        related_name="shopping_lists",
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name="Рецепт",
        related_name="shopping_lists",
    )

    class Meta(CustomMeta):
        verbose_name = "Список покупок"
        verbose_name_plural = "Список покупок"

    def __str__(self):
        return f"{self.user} : {self.recipe}"
