from django.conf import settings
from django.urls import include, path

from api.views import (
    IngredientViewSet,
    RecipeViewSet,
    SubscriptionViewSet,
    TagViewSet,
    UserViewSet
)

if settings.DEBUG:
    from rest_framework.routers import DefaultRouter as Router
else:
    from rest_framework.routers import SimpleRouter as Router


app_name = 'api'

router_v1 = Router()
router_v1.register(
    'users',
    UserViewSet,
    basename='users'
)
router_v1.register(
    'ingredients',
    IngredientViewSet,
    basename='ingredients'
)
router_v1.register(
    'tags',
    TagViewSet,
    basename='tags'
)
router_v1.register(
    'recipes',
    RecipeViewSet,
    basename='recipes'
)
urlpatterns = [
    path('users/subscriptions/', SubscriptionViewSet.as_view()),
    path('auth/', include('djoser.urls.authtoken')),
    path('', include(router_v1.urls)),
]
