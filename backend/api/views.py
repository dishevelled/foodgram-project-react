from api.filters import (IngredientSearchFilter, RecipeFilter)
from api.pagination import PageNumberPagination
from api.permissions import IsAdminOrReadOnly, IsOwnerOrReadOnly
from api.serializers import (CropRecipeSerializer, IngredientSerializer,
                             RecipeSerializer, TagSerializer)
from recipes.models import (
    Cart,
    Favorite,
    Ingredient,
    IngredientAmount,
    Recipe,
    Tag)
from django.http import HttpResponse
from django.shortcuts import get_object_or_404

from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ReadOnlyModelViewSet


class TagsViewSet(ReadOnlyModelViewSet):
    permission_classes = (IsAdminOrReadOnly,)
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None


class IngredientsViewSet(ReadOnlyModelViewSet):
    permission_classes = (IsAdminOrReadOnly,)
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = (IngredientSearchFilter,)
    search_fields = ("^name",)
    pagination_class = None


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    pagination_class = PageNumberPagination
    filterset_class = RecipeFilter
    permission_classes = [IsOwnerOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(
        detail=True,
        methods=["post", "delete"],
        permission_classes=[IsAuthenticated],
    )
    def favorite(self, request, pk=None):
        if request.method == "POST":
            return self.add_obj(Favorite, request.user, pk)
        if request.method == "DELETE":
            return self.delete_obj(Favorite, request.user, pk)
        return None

    @action(
        detail=True,
        methods=["post", "delete"],
        permission_classes=[IsAuthenticated],
    )
    def shopping_cart(self, request, pk=None):
        if request.method == "POST":
            return self.add_obj(Cart, request.user, pk)
        if request.method == "DELETE":
            return self.delete_obj(Cart, request.user, pk)
        return None

    @action(
        detail=False,
        methods=["get"],
        permission_classes=[IsAuthenticated],
    )
    def download_shopping_cart(self, request):
        final_list = {}
        ingredients = IngredientAmount.objects.filter(
            recipe__cart__user=request.user
        ).values_list(
            "ingredient__name",
            "ingredient__measurement_unit",
            "amount",
        )
        for item in ingredients:
            name, measurement_unit, amount = item
            if name in final_list:
                final_list[name]["amount"] += amount
            else:
                final_list[name] = {
                    "measurement_unit": measurement_unit,
                    "amount": amount,
                }
        response = HttpResponse(content_type="application/pdf")
        response["Content-Disposition"] = (
            "attachment; " 'filename="shopping_list.pdf"'
        )
        self.show_page(final_list, response)
        return response

    def show_page(self, final_list, response):
        pdfmetrics.registerFont(
            TTFont("Roboto", "Roboto.ttf", "UTF-8")
        )
        page = canvas.Canvas(response)
        page.setFont("Roboto", size=24)
        page.drawString(
            200, 800, "Список ингредиентов"
        )
        page.setFont("Roboto", size=16)
        height = 750
        for index, (name, data) in enumerate(final_list.items(), 1):
            page.drawString(
                75,
                height,
                f'<{index}> {name} - {data["amount"]},'
                f' {data["measurement_unit"]}',
            )
            height -= 25
        page.showPage()
        page.save()

    def add_obj(self, model, user, pk):
        if model.objects.filter(user=user, recipe__id=pk).exists():
            return Response(
                {"errors": "The recipes has already added to list"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        recipe = get_object_or_404(Recipe, id=pk)
        model.objects.create(user=user, recipe=recipe)
        serializer = CropRecipeSerializer(recipe)
        return Response(
            serializer.data, status=status.HTTP_201_CREATED
        )

    def delete_obj(self, model, user, pk):
        obj = model.objects.filter(user=user, recipe__id=pk)
        count, _ = obj.delete()
        if count:
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(
            {"errors": "The recipes has been deleted"},
            status=status.HTTP_400_BAD_REQUEST,
        )
