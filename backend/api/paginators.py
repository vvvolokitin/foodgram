from rest_framework.pagination import PageNumberPagination

from core.constants_api import PAGE_SIZE


class PageLimitPagination(PageNumberPagination):
    """Пагинация."""

    page_size_query_param = 'limit'
    page_size = PAGE_SIZE
