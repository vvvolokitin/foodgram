from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth import get_user_model

from users.models import Subscription

User = get_user_model()


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = (
        'username',
        'email',
        'first_name',
        'last_name',
        'avatar',
    )
    # list_editable = ('role',)
    search_fields = (
        'username',
        'email'
    )
    list_display_links = ('username',)
    empty_value_display = 'Не задано'


@admin.register(Subscription)
class SubscriptionAdmin(BaseUserAdmin):
    list_display = (
        'user',
        'author',
    )
    search_fields = (
        'user',
        'author'
    )
    empty_value_display = 'Не задано'
