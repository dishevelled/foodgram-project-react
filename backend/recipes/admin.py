from django.contrib import admin
from recipes.models import (
    Cart,
    Favorite,
    Ingredient,
    Recipe,
    Tag,
    IngredientAmount
)


class TagAdmin(admin.ModelAdmin):
    list_display = ("name", "color", "slug")


class IngredientAdmin(admin.ModelAdmin):
    list_display = ("name", "measurement_unit")
    list_filter = ("name",)
    search_fields = ("name",)


class IngredientsInline(admin.TabularInline):
    model = IngredientAmount
    extra = 1


class RecipeAdmin(admin.ModelAdmin):
    list_display = ("name", "author", "count_favorites")
    list_filter = ("author", "name", "tags")
    inlines = [
        IngredientsInline
    ]

    def count_favorites(self, obj):
        return obj.favorites.count()


admin.site.register(Tag, TagAdmin)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Cart)
admin.site.register(Favorite)
