from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


from core.constants_recipes import (
    MAX_AMOUNT,
    MAX_COOKING_TIME,
    MAX_LENGHT_MEASUREMENT_LENGTH,
    MAX_LENGTH_INGREDINET_NAME,
    MAX_LENGTH_RECIPE_NAME,
    MAX_LENGTH_TAG_NAME,
    MIN_AMOUNT,
    MIN_COOKING_TIME
)
from users.models import User


class Ingredient(models.Model):
    """Модель ингредиентов."""

    name = models.CharField(
        verbose_name='Название',
        max_length=MAX_LENGTH_INGREDINET_NAME,
        help_text='Выберите ингредиент'
    )
    measurement_unit = models.CharField(
        verbose_name='Единица изменения',
        max_length=MAX_LENGHT_MEASUREMENT_LENGTH,
        help_text='Выберите единицу измерения'
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        ordering = ('name',)
        constraints = (
            models.UniqueConstraint(
                fields=('name', 'measurement_unit'),
                name='unique_name_measurement_unit'
            ),
        )

    def __str__(self):
        return self.name


class Tag(models.Model):
    """Модель тегов."""

    name = models.CharField(
        verbose_name='Название',
        max_length=MAX_LENGTH_TAG_NAME,
        unique=True,
        help_text='Выберите тег'
    )
    slug = models.SlugField(
        verbose_name='Слаг',
        unique=True,
        help_text=(
            'Идентификатор для слага; '
            'разрешены символы латиницы, цифры, дефис и подчёркивание.'
        )
    )

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'
        ordering = ('name',)

    def __str__(self):
        return self.name


class Recipe(models.Model):
    """Модель рецептов."""

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='author_recipe',
        verbose_name='Автор'
    )
    name = models.CharField(
        verbose_name='Название',
        max_length=MAX_LENGTH_RECIPE_NAME,
        help_text='Название рецепта'
    )
    image = models.ImageField(
        verbose_name='Картинка',
        upload_to='recipes/images',
        help_text='Изображение рецепта.'
    )
    text = models.TextField(
        verbose_name='Описание',
        help_text='Описание рецепта.'
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        related_name='ingredient_recipe',
        through='RecipeIngredient',
        verbose_name='Ингредиенты',
        help_text='Выберите ингредиенты.'
    )
    tags = models.ManyToManyField(
        Tag,
        related_name='tags_recipe',
        verbose_name='Теги',
        help_text='Выберите теги.'
    )
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name='Время приготовления',
        validators=(
            MinValueValidator(MIN_COOKING_TIME),
            MaxValueValidator(MAX_COOKING_TIME)
        ),
        help_text='Время приготовления'
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата публикации',
    )

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ('-pub_date',)

    def save(self, *args, **kwargs):
        if not self.id:
            self.id = uuid.uuid4()
        super().save(*args, **kwargs)

    def clean(self):
        if self.ingredients.count() == 0:
            raise ValidationError(
                'Необходимо указать хотя бы один ингредиент'
            )

    def __str__(self):
        return self.name


class RecipeIngredient(models.Model):
    """Модель взаимосвязи ингредиентов и рецептов."""

    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='recipe_recipeingredients',
        verbose_name='Рецепт'
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name='recipe_recipeingredients',
        verbose_name='Ингредиент'
    )
    amount = models.PositiveSmallIntegerField(
        verbose_name='Количество',
        validators=(
            MinValueValidator(MIN_AMOUNT),
            MaxValueValidator(MAX_AMOUNT)
        )
    )

    class Meta:
        verbose_name = 'Количество ингредиента'
        verbose_name_plural = 'Количество ингредиентов'
        constraints = (
            models.UniqueConstraint(
                fields=('recipe', 'ingredient'),
                name='unique_recipe_ingredient'),
        )


class BaseModel(models.Model):
    """Базовая модель."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Пользователь'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт'
    )

    constraints = (
        models.UniqueConstraint(
            fields=('user', 'recipe'),
            name='unique_user_recipe'
        ),
    )

    class Meta:
        abstract = True


class Favorite(BaseModel):
    """Модель избранного."""

    class Meta:
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранные'
        default_related_name = 'favorites'


class ShoppingCart(BaseModel):
    """Модель списка покупок"""

    class Meta:
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Списки покупок'
        ordering = ('user',)
        default_related_name = 'shopping_cart'
