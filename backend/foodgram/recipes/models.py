from django.db import models

from users.models import User


class Tag(models.Model):
    name = models.CharField(
        max_length=50,
        unique=True,
        verbose_name="Название тэга",
    )
    color = models.CharField(
        max_length=7,
        unique=True,
        verbose_name="Цвет",
    )
    slug = models.SlugField(
        max_length=50,
        unique=True,
        verbose_name="Идентификатор тэга",
    )

    class Meta:
        verbose_name = "Тэг"
        verbose_name_plural = "Тэги"

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    name = models.CharField(
        max_length=100,
        verbose_name="Название ингредиента",
    )
    unit = models.CharField(
        max_length=20,
        verbose_name="Единица измерения",
    )

    class Meta:
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
    title = models.CharField(
        max_length=250,
        verbose_name="Назавание рецепта",
    )
    image = models.ImageField(
        upload_to="recipes/",
        verbose_name="Картинка",
    )
    description = models.TextField(
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
    cooking_time = models.PositiveIntegerField(
        verbose_name="Время приготовления",
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата публикации"
    )

    class Meta:
        ordering = ("-pub_date",)
        verbose_name = "Рецепт"
        verbose_name_plural = "Рецепты"

    def __str__(self):
        return self.title


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE
    )
    quantity = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Количество ингредиентов",
    )

    def __str__(self):
        return f"{self.recipe} : {self.ingredient}"


class Favorite(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name="Пользователь",
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name="Рецепт",
    )

    class Meta:
        verbose_name = "Список избранного"
        verbose_name_plural = "Список избранного"

    def __str__(self):
        return f"{self.user} : {self.recipe}"


class ShoppingList(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name="Пользователь",
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name="Рецепт",
    )

    class Meta:
        verbose_name = "Список покупок"
        verbose_name_plural = "Списки покупок"

    def __str__(self):
        return f"{self.user} : {self.recipe}"
