from django.urls import path
from . import apis


urlpatterns = [
    path('<query>', apis.search_query, name='search_query'),
]
