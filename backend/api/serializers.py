from django.shortcuts import get_object_or_404
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from recipes.models import Ingredient, IngredientAmount, Recipe, Tag
from users.models import Subscription
from users.serializers import RegisteredUserSerializer


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = "__all__"


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = "__all__"


class IngredientAmountSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source="ingredient.id")
    name = serializers.ReadOnlyField(source="ingredient.name")
    measurement_unit = serializers.ReadOnlyField(source="ingredient.measurement_unit")

    class Meta:
        model = IngredientAmount
        fields = ("id", "name", "measurement_unit", "amount")
        validators = [
            UniqueTogetherValidator(
                queryset=IngredientAmount.objects.all(),
                fields=["ingredient", "recipes"],
            )
        ]


class RecipeSerializer(serializers.ModelSerializer):
    image = Base64ImageField()
    tags = TagSerializer(read_only=True, many=True)
    author = RegisteredUserSerializer(read_only=True)
    ingredients = IngredientAmountSerializer(
        source="ingredientamount_set",
        many=True,
        read_only=True,
    )
    is_favorite = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            "id",
            "tags",
            "author",
            "ingredients",
            "is_favorite",
            "is_in_shopping_cart",
            "name",
            "image",
            "text",
            "cooking_time",
        )

    def get_is_favorite(self, obj):
        user = self.context.get("request").user
        if user.is_anonymous:
            return False
        return Recipe.objects.filter(id=obj.id, favorites__user=user).exists()

    def get_is_in_shopping_cart(self, obj):
        user = self.context.get("request").user
        if user.is_anonymous:
            return False
        return Recipe.objects.filter(cart__user=user, id=obj.id).exists()

    def validate(self, data):
        ingredients = self.initial_data.get("ingredients")
        if not ingredients:
            raise serializers.ValidationError(
                {"ingredients": "Нужен хоть один ингридиент для рецепта"}
            )
        ingredient_list = []
        for ingredient_item in ingredients:
            ingredient = get_object_or_404(Ingredient, id=ingredient_item["id"])
            if ingredient in ingredient_list:
                raise serializers.ValidationError("Ингридиенты должны быть уникальными")
            ingredient_list.append(ingredient)
            if int(ingredient_item["amount"]) < 0:
                raise serializers.ValidationError(
                    {
                        "ingredients": (
                            "Убедитесь, что значение количества" "ингредиента больше 0"
                        )
                    }
                )
        data["ingredients"] = ingredients
        return data

    def create_ingredients(self, ingredients, recipe):
        elements = []
        for ingredient in ingredients:
            elements.append(
                IngredientAmount(
                    recipe=recipe,
                    ingredient_id=ingredient.get("id"),
                    amount=ingredient.get("amount"),
                )
            )
        IngredientAmount.objects.bulk_create(elements)

    def create_tags(self, tags, recipe):
        recipe.tags.set(tags)

    def create(self, validated_data):
        image = validated_data.pop("image")
        ingredients_data = validated_data.pop("ingredients")
        recipe = Recipe.objects.create(image=image, **validated_data)
        tags_data = self.initial_data.pop("tags")
        self.create_tags(tags_data, recipe)
        self.create_ingredients(ingredients_data, recipe)
        return recipe

    def update(self, instance, validated_data):
        instance.tags.clear()
        IngredientAmount.objects.filter(recipe=instance).delete()
        self.create_tags(self.initial_data.pop("tags"), instance)
        self.create_ingredients(validated_data.pop("ingredients"), instance)
        return super().update(instance, validated_data)


class CropRecipeSerializer(serializers.ModelSerializer):
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = ("id", "name", "image", "cooking_time")
        read_only_fields = ("id", "name", "image", "cooking_time")


class FollowSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source="author.id")
    email = serializers.ReadOnlyField(source="author.email")
    username = serializers.ReadOnlyField(source="author.username")
    first_name = serializers.ReadOnlyField(source="author.first_name")
    last_name = serializers.ReadOnlyField(source="author.last_name")
    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = Subscription
        fields = (
            "id",
            "email",
            "username",
            "first_name",
            "last_name",
            "is_subscribed",
            "recipes",
            "recipes_count",
        )

    def get_is_subscribed(self, obj):
        return Subscription.objects.filter(user=obj.user, author=obj.author).exists()

    def get_recipes(self, obj):
        request = self.context.get("request")
        limit = request.GET.get("recipes_limit")
        queryset = Recipe.objects.filter(author=obj.author)
        if limit:
            queryset = queryset[: int(limit)]
        return CropRecipeSerializer(queryset, many=True).data

    def get_recipes_count(self, obj):
        return Recipe.objects.filter(author=obj.author).count()
