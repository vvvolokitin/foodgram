from rest_framework.pagination import PageNumberPagination

from core.constants_api import PAGE_SIZE, PAGE_SIZE_QUERY_PARAM


class PageLimitPagination(PageNumberPagination):
    """Пагинация."""

    page_size_query_param = PAGE_SIZE_QUERY_PARAM
    page_size = PAGE_SIZE
