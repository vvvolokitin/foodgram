import os

from dotenv import load_dotenv
from django.contrib.auth import get_user_model
from django.db.models import Sum
from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet as DjoserViewSet
from rest_framework import status, viewsets
from rest_framework.decorators import action
# from rest_framework.generics import ListAPIView
from rest_framework.permissions import (
    SAFE_METHODS,
    AllowAny,
    IsAuthenticated,
    IsAuthenticatedOrReadOnly
)
from rest_framework.response import Response
from urlshortner.utils import shorten_url

from api.filters import IngredientFilter, RecipeFilter
from api.paginators import PageLimitPagination
from api.permissions import IsAuthorAdminOrReadOnly
from api.serializers import (
    AvatarSerializer,
    IngredientSerializer,
    RecipeCreateSerializer,
    RecipeSerializer,
    RecipesShortSerializer,
    SubscribedSerislizer,
    SubscriptionsSerializer,
    TagSerializer,
    UserCreateSerializer,
    UserSerializer
)
from recipes.models import (
    Favorite,
    Ingredient,
    Recipe,
    RecipeIngredient,
    ShoppingCart,
    Tag
)
from users.models import Subscription


load_dotenv()
User = get_user_model()


class UserViewSet(DjoserViewSet):
    """Вьюсет пользователя."""

    queryset = User.objects.all()
    permission_classes = (IsAuthenticatedOrReadOnly,)
    pagination_class = PageLimitPagination

    def get_serializer_class(self):
        if self.action == 'create':
            return UserCreateSerializer
        return UserSerializer

    def get_permissions(self):
        if self.action == 'me':
            return (IsAuthenticated(),)
        return super().get_permissions()

    @action(
        ['put'],
        detail=False,
        permission_classes=(IsAuthenticated,),
        url_path='me/avatar',
        url_name='avatar',
    )
    def avatar(self, request):
        """Метод добавления аватара."""
        serializer = AvatarSerializer(
            self.request.user,
            data=request.data
        )
        if (serializer.is_valid() and 'avatar' in request.data):
            serializer.save()
            return Response(
                serializer.data,
                status=status.HTTP_200_OK
            )
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

    @avatar.mapping.delete
    def delete_avatar(self, request):
        """Метод удаления аватара."""
        serializer = AvatarSerializer(
            self.request.user,
            data=request.data
        )
        if serializer.is_valid(raise_exception=True):
            request.user.avatar.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        ['post'],
        detail=True,
        permission_classes=(IsAuthenticated,),
        url_path='subscribe',
        url_name='subscribe'
    )
    def subscribe(self, request, id):
        """Метод управления подписками."""
        user = request.user
        author = get_object_or_404(User, id=id)
        serializer = SubscribedSerislizer(
            data={
                'user': user.id,
                'author': author.id
            },
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED
        )

    @subscribe.mapping.delete
    def delete_subscribe(self, request, id):
        user = request.user
        author = get_object_or_404(User, id=id)
        change_subscription_status = Subscription.objects.filter(
            user=user.id,
            author=author.id
        )
        if change_subscription_status.exists():
            change_subscription_status.delete()
            return Response(
                f'Вы отписались от {author}.',
                status=status.HTTP_204_NO_CONTENT
            )
        return Response(
            f'Вы не подписаны на {author}',
            status=status.HTTP_400_BAD_REQUEST
        )

    @action(
        methods=['get', ],
        detail=False,
        url_path='subscriptions'
    )
    def subscriptions(self, request):
        user = request.user
        queryset = User.objects.filter(author__user=user)
        pages = self.paginate_queryset(queryset)
        serializer = SubscriptionsSerializer(
            pages, many=True, context={"request": request}
        )
        return self.get_paginated_response(serializer.data)

    # class SubscriptionViewSet(ListAPIView):
    #     """Вьюсет подписок."""
    #     serializer_class = SubscriptionsSerializer
    #     permission_classes = (IsAuthenticated,)
    #     pagination_class = PageLimitPagination

    #     def get_queryset(self):
    #         user = self.request.user
    #         return user.subscriber.all()


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """Вьюсет ингредиентов."""

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (AllowAny,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientFilter
    search_fields = ('name',)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """Вьюсет тегов."""

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (AllowAny,)


class RecipeViewSet(viewsets.ModelViewSet):
    """Вьюсет рецептов."""

    queryset = Recipe.objects.all()
    permission_classes = (IsAuthorAdminOrReadOnly,)
    pagination_class = PageLimitPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        if self.request.method in SAFE_METHODS:
            return RecipeSerializer
        return RecipeCreateSerializer

    def add_recipe(self, request, pk, model):
        """Метод добавления рецепта в избранное/список покупок."""
        user = request.user
        try:
            recipe = get_object_or_404(Recipe, id=pk)
        except Http404:
            return Response(
                'Рецепт не найден',
                status=status.HTTP_400_BAD_REQUEST
            )
        if model.objects.filter(
            user=user,
            recipe=recipe
        ).exists():
            return Response(
                {'errors': f'Рецепт-"{recipe.name}" уже добавлен!'},
                status=status.HTTP_400_BAD_REQUEST
            )
        model.objects.create(
            user=user,
            recipe=recipe
        )
        serializer = RecipesShortSerializer(recipe)
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED
        )

    def delete_recipe(self, request, pk, model):
        """Метод удаления рецепта из избрнного/списка покупок."""
        user = request.user
        try:
            recipe = get_object_or_404(
                Recipe,
                id=pk
            )
        except Http404:
            return Response(
                'Рецепт не найден',
                status=status.HTTP_404_NOT_FOUND
            )
        obj = model.objects.filter(
            user=user,
            recipe=recipe
        )
        if obj.exists():
            obj.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(
            {'errors': f'В избранном нет рецепта "{recipe.name}"'},
            status=status.HTTP_400_BAD_REQUEST
        )

    @action(
        ['post'],
        detail=True,
        permission_classes=[IsAuthenticated],
        url_path='favorite',
        url_name='favorite'
    )
    def favorite(self, request, pk):
        """Метод добавления в избранное."""
        try:
            get_object_or_404(Recipe, id=pk)
        except Http404:
            return Response(
                'Рецепт не найден',
                status=status.HTTP_404_NOT_FOUND
            )
        return self.add_recipe(
            request,
            pk,
            Favorite
        )

    @favorite.mapping.delete
    def delete_favorite(self, request, pk):
        """Метод удаления избранного."""
        try:
            get_object_or_404(Recipe, id=pk)
        except Http404:
            return Response(
                'Рецепт не найден',
                status=status.HTTP_404_NOT_FOUND
            )
        return self.delete_recipe(
            request,
            pk,
            Favorite
        )

    @action(
        ['post'],
        detail=True,
        permission_classes=[IsAuthenticated],
        url_path='shopping_cart',
        url_name='shopping_cart'
    )
    def shopping_cart(self, request, pk):
        """Метод добавления в спискок покупок."""
        try:
            get_object_or_404(Recipe, id=pk)
        except Http404:
            return Response(
                'Рецепт не найден',
                status=status.HTTP_404_NOT_FOUND
            )
        return self.add_recipe(
            request,
            pk,
            ShoppingCart
        )

    @shopping_cart.mapping.delete
    def delete_shopping_cart(self, request, pk):
        """Метод удаления из списка покупок."""
        try:
            get_object_or_404(Recipe, id=pk)
        except Http404:
            return Response(
                'Рецепт не найден',
                status=status.HTTP_404_NOT_FOUND
            )
        return self.delete_recipe(
            request,
            pk,
            ShoppingCart
        )

    @staticmethod
    def shopping_cart_to_list(ingredients):
        """Метод создания списка покупок."""
        shopping_cart_list = ''
        for ingredient in ingredients:
            shopping_cart_list += (
                f'{ingredient["ingredient__name"]}: '
                f'{ingredient["sum"]} '
                f'({ingredient["ingredient__measurement_unit"]})\n'
            )
        return shopping_cart_list

    @action(
        ['get'],
        detail=False,
        permission_classes=[IsAuthenticated, ],
        url_path='download_shopping_cart',
        url_name='download_shopping_cart',
    )
    def download_shopping_cart(self, request):
        """Метод загрузки списка покупок."""
        ingredients = RecipeIngredient.objects.filter(
            recipe__shopping_cart__user=request.user
        ).values(
            'ingredient__name',
            'ingredient__measurement_unit'
        ).annotate(sum=Sum('amount'))
        shopping_cart_list = self.shopping_cart_to_list(ingredients)
        return HttpResponse(
            shopping_cart_list,
            content_type='text/plain'
        )

    @action(detail=True, url_path='get-link')
    def get_link(self, request, pk=None):
        """Метод получения короткой ссылки."""
        try:
            get_object_or_404(Recipe, id=pk)
        except Http404:
            return Response(
                'Рецепт не найден',
                status=status.HTTP_404_NOT_FOUND
            )
        host = os.getenv(
            'URL_HOST',
            default='https://localhost'
        )
        long_url = f'{host}/recipes/{pk}/'
        short_link = shorten_url(
            long_url,
            is_permanent=True
        )
        return Response(
            {'short-link': f'{host}/s/{short_link}', }
        )


# class SubscriptionViewSet(ListAPIView):
#     """Вьюсет подписок."""
#     serializer_class = SubscriptionsSerializer
#     permission_classes = (IsAuthenticated,)
#     pagination_class = PageLimitPagination

#     def get_queryset(self):
#         user = self.request.user
#         return user.subscriber.all()
