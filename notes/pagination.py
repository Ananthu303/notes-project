from rest_framework.pagination import PageNumberPagination

class VersionPagination(PageNumberPagination):
    page_size = 5
