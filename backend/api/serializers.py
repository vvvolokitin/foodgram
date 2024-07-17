from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from djoser.serializers import UserSerializer as DjoserUserSerializer
from rest_framework import serializers

from api.fields import Base64ImageField
from recipes.models import (
    Favorite,
    Ingredient,
    Recipe,
    RecipeIngredient,
    ShoppingCart,
    Tag
)
from users.models import Subscription


User = get_user_model()


class UserSerializer(DjoserUserSerializer):
    """Сериализатор пользователя."""

    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'id',
            'username',
            'email',
            'first_name',
            'last_name',
            'avatar',
            'is_subscribed',
        )

    def get_is_subscribed(self, obj):
        user = self.context.get('request').user
        return (
            user.is_authenticated
            and Subscription.objects.filter(
                author=obj,
                user=user
            ).exists()
        )


class UserCreateSerializer(DjoserUserSerializer):
    """Сериализатор создания пользователя."""

    class Meta:
        model = User

        fields = (
            'id',
            'username',
            'email',
            'first_name',
            'last_name',
            'avatar',
            'password',
        )

    def validate_username(self, username):
        if username == 'me':
            raise serializers.ValidationError(
                'Имя пользователя не может быть "me".'
            )
        return username

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)


class AvatarSerializer(serializers.Serializer):
    """Сериализатор аватара."""

    avatar = Base64ImageField()

    def update(self, instance, validated_data):
        instance.avatar = validated_data.get('avatar', instance.avatar)
        return instance

# class AvatarSerializer(serializers.ModelSerializer):
#     """Сериализатор аватара."""

#     avatar = Base64ImageField()

#     class Meta:
#         model = User
#         fields = ('avatar',)


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор ингредиентов."""

    class Meta:
        model = Ingredient
        fields = (
            'id',
            'name',
            'measurement_unit'
        )


class TagSerializer(serializers.ModelSerializer):
    """Сериализаторо тегов."""

    class Meta:
        model = Tag
        fields = (
            'id',
            'name',
            'slug'
        )


class RecipreIngredientSerializer(serializers.ModelSerializer):
    """Сериализатор ингредиентов рецептов."""

    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )
    amount = serializers.IntegerField()

    def validate_amount(self, value):
        if value < 1:
            raise serializers.ValidationError(
                'Количество ингредиента должно быть больше 0!'
            )
        return value

    class Meta:
        model = RecipeIngredient
        fields = (
            'id',
            'name',
            'measurement_unit',
            'amount'
        )


class RecipeIngredientCreateSerializer(serializers.ModelSerializer):
    """Сериализатор создания ингредиентов рецептов."""

    id = serializers.IntegerField()
    amount = serializers.IntegerField()

    def validate_amount(self, value):
        if value < 1:
            raise serializers.ValidationError(
                'Количество ингредиента должно быть больше 0!'
            )
        return value

    class Meta:
        model = RecipeIngredient
        fields = (
            'id',
            'amount'
        )


class RecipeSerializer(serializers.ModelSerializer):
    """Сериализатор рецептов."""

    image = Base64ImageField()
    author = UserSerializer(read_only=True)
    tags = TagSerializer(many=True)
    ingredients = RecipreIngredientSerializer(
        many=True,
        source='recipe_recipeingredients'
    )
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'ingredients',
            'tags',
            'image',
            'name',
            'author',
            'text',
            'cooking_time',
            'is_favorited',
            'is_in_shopping_cart'
        )

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        return Favorite.objects.filter(
            user=request.user,
            recipe=obj
        ).exists()

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        return ShoppingCart.objects.filter(
            user=request.user,
            recipe=obj
        ).exists()


class RecipeCreateSerializer(serializers.ModelSerializer):
    """Сериализатор создания рецептов."""

    image = Base64ImageField()
    ingredients = RecipeIngredientCreateSerializer(many=True)
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True
    )
    author = UserSerializer(read_only=True)

    class Meta:
        model = Recipe
        fields = (
            'ingredients',
            'tags',
            'image',
            'name',
            'text',
            'author',
            'cooking_time'
        )

    def validate_tags(self, value):
        if len(value) == 0:
            raise serializers.ValidationError(
                'Должен быть отмечено не меньше 1 тега'
            )
        tag_list = []
        for val in value:
            if val in tag_list:
                raise serializers.ValidationError(
                    'Теги должны быть уникальными'
                )
            tag_list.append(val)
        return value

    def validate_ingredients(self, value):
        if not value:
            raise serializers.ValidationError(
                {
                    'ingredients': 'Должен быть хотя бы один ингредиент'
                }
            )

        ingredient_list = []
        for val in value:
            try:
                ingredient = Ingredient.objects.get(id=val['id'])
            except Ingredient.DoesNotExist:
                raise serializers.ValidationError(
                    'Введен не существующий ингредиент'
                )
            if ingredient in ingredient_list:
                raise serializers.ValidationError(
                    'Ингридиенты должны быть уникальными'
                )
            ingredient_list.append(ingredient)
            if val['amount'] <= 0:
                raise serializers.ValidationError(
                    {
                        'ingredients':
                        'Значение ингредиента должно быть больше 0'
                    }
                )
        return value

    def validate_cooking_time(self, value):
        if value <= 0:
            raise serializers.ValidationError(
                'Время приготовления должно быть больше 0!'
            )
        return value

    def create_ingredients(self, ingredients, recipe):
        for element in ingredients:
            id = element['id']
            ingredient = Ingredient.objects.get(pk=id)
            amount = element['amount']
            RecipeIngredient.objects.create(
                ingredient=ingredient,
                recipe=recipe,
                amount=amount
            )

    def create_tags(self, tags, recipe):
        recipe.tags.set(tags)

    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        user = self.context.get('request').user
        recipe = Recipe.objects.create(
            **validated_data,
            author=user
        )
        self.create_ingredients(
            ingredients,
            recipe
        )
        self.create_tags(
            tags,
            recipe
        )
        return recipe

    def update(self, instance, validated_data):
        instance.ingredients.clear()
        self.create_ingredients(
            validated_data.pop('ingredients'),
            instance
        )
        return super().update(
            instance,
            validated_data
        )

    def to_representation(self, instance):
        serializer = RecipeSerializer(
            instance,
            context={
                'request': self.context.get('request')
            }
        )
        return serializer.data


class FavoriteSerializer(serializers.ModelSerializer):
    """Сериализатор избранных рецептов."""

    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
            'image',
            'cooking_time'
        )
        validators = (
            serializers.UniqueTogetherValidator
            (
                queryset=model.objects.all(),
                fields=('recipe', 'user'),
                message='Рецепт уже добавлен!'
            ),
        )


class ShoppingCartSerializer(serializers.ModelSerializer):
    """Сериализатор списка покупок."""

    class Meta:
        model = ShoppingCart
        fields = (
            'id',
            'user',
            'recipe'
        )
        validators = (
            serializers.UniqueTogetherValidator
            (
                queryset=model.objects.all(),
                fields=('recipe', 'user'),
                message='Рецепт уже добавлен!'
            ),
        )

    def validate(self, data):
        recipe = data['recipe']
        if not recipe:
            raise ValidationError('Рецепт не может быть пустым!')
        if recipe in self.context['request'].user.shopping_cart.recipe.all():
            raise ValidationError('Данный рецепт уже существует!')
        return data


class RecipesShortSerializer(serializers.ModelSerializer):
    """Сериализатор рецептов, короткая версия."""

    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
            'image',
            'cooking_time'
        )


class FollowSerializer(serializers.ModelSerializer):
    """Сериализатор подписок."""

    class Meta:
        model = Subscription
        fields = (
            'user',
            'author'
        )

    def to_representation(self, instance):
        return ShowFollowSerializer(
            instance.author,
            context=self.context
        ).data


class ShowFollowSerializer(serializers.ModelSerializer):
    """Сериализатор отображения подписок."""

    recipes = RecipesShortSerializer(
        many=True,
        read_only=True
    )
    recipes_count = serializers.SerializerMethodField()
    is_subscribed = serializers.SerializerMethodField(default=True)

    class Meta:
        model = Subscription
        fields = (
            'id',
            'user',
            'author',
            'is_subscribed',
            'recipes',
            'recipes_count'
        )
        read_only_fields = ('__all__',)

    def get_recipes(self, obj):
        request = self.context.get('request')
        if request.GET.get('recipes_limit'):
            recipes_limit = int(request.GET.get('recipes_limit'))
            queryset = Recipe.objects.filter(author=obj.author)[:recipes_limit]
        else:
            queryset = Recipe.objects.filter(author=obj.author)
        serializer = RecipesShortSerializer(
            queryset,
            many=True,
            read_only=True
        )
        return serializer.data

    def get_recipes_count(self, obj):
        return obj.recipes.count()

    def get_is_subscribed(self, obj):
        user = self.context.get('request').user
        if user.is_authenticated:
            if isinstance(obj, User):
                return Subscription.objects.filter(
                    author=obj,
                    user=user
                ).exists()
            return True
        return False


class SubscriptionsSerializer(UserSerializer):
    """Сериализатор подписок пользователя."""

    email = serializers.ReadOnlyField(source="author.email")
    id = serializers.ReadOnlyField(source="author.id")
    username = serializers.ReadOnlyField(source="author.username")
    first_name = serializers.ReadOnlyField(source="author.first_name")
    last_name = serializers.ReadOnlyField(source="author.last_name")
    avatar = serializers.ImageField(source='author.avatar')
    recipes = serializers.SerializerMethodField(method_name='get_recipes')
    recipes_count = serializers.SerializerMethodField(
        method_name='get_recipes_count'
    )
    is_subscribed = serializers.SerializerMethodField(
        method_name='get_is_subscribed'
    )

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'avatar',
            'is_subscribed',
            'recipes',
            'recipes_count'
        )

    def get_recipes(self, obj):
        request = self.context.get('request')
        if request.GET.get('recipes_limit'):
            recipe_limit = int(request.GET.get('recipes_limit'))
            queryset = Recipe.objects.filter(author=obj.author)[:recipe_limit]
        else:
            queryset = Recipe.objects.filter(author=obj.author)
        serializer = RecipesShortSerializer(
            queryset,
            many=True,
            read_only=True
        )
        return serializer.data

    def get_recipes_count(self, obj):
        """Количество рецептов автора."""
        return Recipe.objects.filter(author=obj.author).count()

    def get_is_subscribed(self, obj):
        """Метод проверки подписки"""
        request = self.context.get('request')
        return Subscription.objects.filter(
            author=obj.author, user=request.user).exists()


class SubscribedSerislizer(serializers.ModelSerializer):
    """Сериализатор подписки."""

    class Meta:
        model = Subscription
        fields = (
            'user',
            'author'
        )

    def to_representation(self, instanсe):
        request = self.context.get('request')
        context = {'request': request}
        serialiser = SubscriptionsSerializer(
            instanсe,
            context=context
        )
        return serialiser.data
