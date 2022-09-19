from colorfield.fields import ColorField
from django.core import validators
from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Ingredient(models.Model):
    name = models.CharField(max_length=200, verbose_name="Название")
    measurement_unit = models.CharField(
        max_length=200, verbose_name="Единица измерения"
    )

    class Meta:
        ordering = ["-id"]
        verbose_name = "Ингредиент"
        verbose_name_plural = "Ингредиенты"
        unique_together = ["name", "measurement_unit"]

    def __str__(self):
        return self.name


class Tag(models.Model):

    name = models.CharField(unique=True,
                            max_length=200,
                            verbose_name="Название тэга")
    color = ColorField(
        unique=True,
        max_length=7,
        verbose_name="Цвет в HEX",
    )
    slug = models.SlugField(unique=True,
                            max_length=200,
                            verbose_name="Уникальный слаг")

    class Meta:
        ordering = ["-id"]
        verbose_name = "Тэг"
        verbose_name_plural = "Тэги"

    def __str__(self):
        return self.name


class Recipe(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="recipes",
        verbose_name="Автор",
    )
    name = models.CharField(max_length=200, verbose_name="Имя")
    image = models.ImageField(upload_to="recipes/", verbose_name="Картинка")
    text = models.TextField(verbose_name="Тестовое описание")
    ingredients = models.ManyToManyField(
        Ingredient,
        through="IngredientAmount",
        verbose_name="Ингредиенты",
        related_name="recipes",
    )
    tags = models.ManyToManyField(
        Tag,
        verbose_name="Тэги",
    )
    cooking_time = models.PositiveSmallIntegerField(
        validators=(
            validators.MinValueValidator(1,
                                         message="Minimum cooking time is 1 minute"),
        ),
        verbose_name="Время приготовления",
    )

    class Meta:
        ordering = ["-id"]
        verbose_name = "Рецепт"
        verbose_name_plural = "Рецепты"


class IngredientAmount(models.Model):
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        verbose_name="Ингредиент",
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name="Рецепт",
    )
    amount = models.PositiveSmallIntegerField(
        validators=(
            validators.MinValueValidator(
                1, message="The minimum number of ingredients is 1"
            ),
        ),
        verbose_name="Количество",
    )

    class Meta:
        ordering = ["-id"]
        constraints = [
            models.UniqueConstraint(
                fields=["ingredient", "recipe"],
                name="unique ingredients recipe",
            )
        ]


class Favorite(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name="Пользователь",
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name="favorites",
        verbose_name="Рецепт",
    )

    class Meta:
        ordering = ["-id"]
        verbose_name = "Избранный"
        verbose_name_plural = "Избранные"
        constraints = [
            models.UniqueConstraint(
                fields=["user", "recipe"],
                name="unique favorite recipe for user",
            )
        ]


class Cart(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="cart",
        verbose_name="Пользователь",
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name="cart",
        verbose_name="Рецепт",
    )

    class Meta:
        ordering = ["-id"]
        verbose_name = "Корзина"
        verbose_name_plural = "В корзине"
        constraints = [
            models.UniqueConstraint(fields=["user", "recipe"],
                                    name="unique cart user"
                                    )
        ]
