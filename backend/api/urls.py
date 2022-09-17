from api.views import IngredientsViewSet, RecipeViewSet, TagsViewSet
from django.urls import include
from django.urls import re_path as path
from rest_framework.routers import DefaultRouter

app_name = "api"

router = DefaultRouter()
router.register("tags", TagsViewSet)
router.register("ingredients", IngredientsViewSet)
router.register("recipes", RecipeViewSet)

urlpatterns = [
    path("", include(router.urls)),
]
