from django.urls import path

from product_app.views import CategoryAPI, ProductCreateAPI, ProductRetrieveUpdateAPI, AddRatingAPI, ProductRatingsAPI, \
    ProductAverageAPI, ProductImageAPI, ProductImageRUDAPI, ProductWiseImageAPI

url_patterns = [
    path("create/category/",CategoryAPI.as_view(),name="categories"),
    path("create/product/",ProductCreateAPI.as_view(),name="products"),
    path("product/<int:pk>/",ProductRetrieveUpdateAPI.as_view(),name="products-rud"),
    path("rate/", AddRatingAPI.as_view()),
    path("ratings/<int:product_id>/", ProductRatingsAPI.as_view()),
    path("avg-rating/<int:product_id>/", ProductAverageAPI.as_view()),
    path("product-images/", ProductImageAPI.as_view()),
    path("product-images/<int:pk>/", ProductImageRUDAPI.as_view()),
    path("product/<int:product_id>/images/", ProductWiseImageAPI.as_view()),
]