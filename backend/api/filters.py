from django_filters.rest_framework import FilterSet, filters
from recipes.models import Recipe, Tag
from rest_framework.filters import SearchFilter
from users.models import User


class IngredientSearchFilter(SearchFilter):
    search_param = "name"


class AuthorAndTagFilter(FilterSet):
    tags = filters.AllValuesMultipleFilter(field_name="tags__slug")
    author = filters.ModelChoiceFilter(queryset=User.objects.all())
    is_favorite = filters.BooleanFilter(method="filter_is_favorite")
    is_in_shopping_cart = filters.BooleanFilter(
        method="filter_is_in_shopping_cart"
    )

    def filter_is_favorite(self, queryset, name, value):
        if value and not self.request.user.is_anonymous:
            return queryset.filter(favorites__user=self.request.user)
        return queryset

    def filter_is_in_shopping_cart(self, queryset, name, value):
        if value and not self.request.user.is_anonymous:
            return queryset.filter(cart__user=self.request.user)
        return queryset

    class Meta:
        model = Recipe
        fields = ("tags", "author")


class RecipeFilter(FilterSet):
    author = filters.ModelChoiceFilter(queryset=User.objects.all())
    tags = filters.ModelMultipleChoiceFilter(
        queryset=Tag.objects.all(),
        field_name='tags__slug',
        to_field_name='slug',
    )
    is_favorite = filters.NumberFilter(method="get_is_favorite")
    is_in_shopping_cart = filters.NumberFilter(
        method="get_is_in_shopping_cart"
    )

    class Meta:
        model = Recipe
        fields = (
            "tags",
            "author",
        )

    def if_user_is_anonymous(func):
        def check_user(self, queryset, name, value, *args, **kwargs):
            if self.request.user.is_anonymous:
                return queryset.none()
            return func(self, queryset, name, value, *args, **kwargs)

        return check_user

    @if_user_is_anonymous
    def get_is_favorite(self, queryset, name, value):
        if value:
            return queryset.filter(favorites__user=self.request.user)
        return queryset

    @if_user_is_anonymous
    def get_is_in_shopping_cart(self, queryset, name, value):
        if value:
            return queryset.filter(cart__user=self.request.user)
        return queryset
