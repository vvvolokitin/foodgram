from django.contrib import admin
from django.contrib.auth import get_user_model

from .models import Subscription

User = get_user_model()

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = (
        'username',
        'email',
        'first_name',
        'last_name',
        'avatar',
        'role',)
    list_editable = ('role',)
    search_fields = (
        'username',
        'email'
    )
    list_display_links = ('username',)
    empty_value_display = 'Не задано'

@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'author',
    )
    search_fields = (
        'user',
        'author'
    )
    empty_value_display = 'Не задано'
