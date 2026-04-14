from django.urls import path

from product_app.views import CategoryAPI, ProductCreateAPI, ProductRetrieveUpdateAPI

url_patterns = [
    path("create/category/",CategoryAPI.as_view(),name="categories"),
    path("create/product/",ProductCreateAPI.as_view(),name="products"),
    path("product/<int:pk>/",ProductRetrieveUpdateAPI.as_view(),name="products-rud"),
]