from django.contrib.auth.models import AbstractUser
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.core.exceptions import ValidationError
from django.db import models

from core.constants_users import (
    MAX_LENGTH_EMAIL,
    MAX_LENGTH_NAME,
    MAX_LENGTH_ROLE,
    ROLES,
    USER
)


class User(AbstractUser):
    """Модель прользователя."""

    email = models.EmailField(
        verbose_name='Адрес электронной почты',
        max_length=MAX_LENGTH_EMAIL,
        unique=True
    )
    username = models.CharField(
        verbose_name='Уникальный юзернейм',
        max_length=MAX_LENGTH_NAME,
        unique=True,
        validators=(UnicodeUsernameValidator(),)
    )
    first_name = models.CharField(
        verbose_name='Имя',
        max_length=MAX_LENGTH_NAME
    )
    last_name = models.CharField(
        verbose_name='Фамилия',
        max_length=MAX_LENGTH_NAME
    )
    avatar = models.ImageField(
        verbose_name='Аватар',
        upload_to='users',
        blank=True
    )
    role = models.CharField(
        verbose_name='Пользовательская роль',
        max_length=MAX_LENGTH_ROLE,
        choices=ROLES,
        default=USER
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = (
        'username',
        'first_name',
        'last_name',
    )

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"
        ordering = ('username',)

    def clean(self):
        if self.username.lower() in ('me', 'em'):
            raise ValidationError(
                'Имя пользователя не может быть "me"'
            )


class Subscription(models.Model):
    """Модель подписки."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscriber',
        verbose_name='Подписчик'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscribed',
        verbose_name='Автор'
    )

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        constraints = (
            models.UniqueConstraint(
                fields=('user', 'author'),
                name='unique_user_subscription'
            ),
            models.CheckConstraint(
                check=~models.Q(user=models.F('author')),
                name='subscribe_to_yourself',
                
            )
        )

    def clean_fields(self, exclude=None):
        super().clean_fields(exclude=exclude)
        if self.user and self.author and self.user == self.author:
            raise ValidationError("Нельзя подписаться на самого себя.")
