from rest_framework import pagination

class ColorPalletesPagination(pagination.PageNumberPagination):
    page_size = 2
