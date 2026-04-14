from django.urls import path

from product_app.views import CategoryAPI

url_patterns = [
    path("create/category/",CategoryAPI.as_view(),name="categories")
]