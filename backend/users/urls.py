from django.urls import include, re_path as path
from rest_framework.routers import DefaultRouter

from users.views import RegisteredUserViewSet

app_name = 'api'

router = DefaultRouter()
router.register('users', RegisteredUserViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
]
