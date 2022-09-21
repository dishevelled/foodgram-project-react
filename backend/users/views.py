from api.pagination import PageNumberPagination
from api.serializers import FollowSerializer
from djoser.views import UserViewSet
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from users.models import Subscription, User
from users.responses import ErrorResponse


class RegisteredUserViewSet(UserViewSet):
    pagination_class = PageNumberPagination
    serializer_class = FollowSerializer

    @action(
        detail=True,
        methods=["post"],
        permission_classes=[IsAuthenticated],
    )
    def subscribe(self, request, id=None):
        user = request.user
        author = get_object_or_404(User, id=id)

        if user == author:
            return ErrorResponse(
                "You can't subscribe to yourself",
                status.HTTP_400_BAD_REQUEST,
            )
        if Subscription.objects.filter(
            user=user, author=author
        ).exists():
            return ErrorResponse(
                "You have already subscribed to this user",
                status.HTTP_400_BAD_REQUEST,
            )

        Subscription.objects.create(user=user, author=author)
        serializer = FollowSerializer(
            author, context={"request": request}
        )
        return Response(
            serializer.data, status=status.HTTP_201_CREATED
        )

    @subscribe.mapping.delete
    def remove_subscribe(self, request, id=None):
        user = request.user

        if user.id == id:
            return ErrorResponse(
                "You can't unsubscribe from yourself",
                status.HTTP_400_BAD_REQUEST,
            )

        author = get_object_or_404(User, id=id)
        follow = Subscription.objects.filter(user=user, author=author)
        if len(follow.delete()):
            return Response(status=status.HTTP_204_NO_CONTENT)

        return ErrorResponse(
            "You have already unsubscribed",
            status.HTTP_400_BAD_REQUEST,
        )

    @action(detail=False, permission_classes=[IsAuthenticated])
    def subscriptions(self, request):
        user = request.user
        queryset = User.objects.filter(follower__user=user)
        pages = self.paginate_queryset(queryset)
        serializer = FollowSerializer(
            pages, many=True, context={"request": request}
        )
        return self.get_paginated_response(serializer.data)
