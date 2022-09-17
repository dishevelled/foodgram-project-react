from django_filters.rest_framework import FilterSet, filters
from recipes.models import Recipe
from rest_framework.filters import SearchFilter

from users.models import User


class IngredientSearchFilter(SearchFilter):
    search_param = "name"


class AuthorAndTagFilter(FilterSet):
    tags = filters.AllValuesMultipleFilter(field_name="tags__slug")
    author = filters.ModelChoiceFilter(queryset=User.objects.all())
    is_favorite = filters.BooleanFilter(method="filter_is_favorite")
    is_in_shopping_cart = filters.BooleanFilter(method="filter_is_in_shopping_cart")

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
