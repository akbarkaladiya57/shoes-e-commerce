from django.urls import path

from product_app.views import CategoryAPI, ProductCreateAPI, ProductRetrieveUpdateAPI, AddRatingAPI, ProductRatingsAPI, \
    ProductAverageAPI, ProductImageAPI, ProductImageRUDAPI, ProductWiseImageAPI, CategoryFilterAPI, \
    ProductLikeListCreateApiview,ProductLikeDetailAPIView,AI_ShoeFinderView

url_patterns = [
    path("categories/",CategoryAPI.as_view(),name="categories"),
    path("products/",ProductCreateAPI.as_view(),name="products"),
    path("product/<int:pk>/",ProductRetrieveUpdateAPI.as_view(),name="products-rud"),
    path("category/filter/",CategoryFilterAPI.as_view(),name="products-by-category"),
    path("rate/", AddRatingAPI.as_view()),
    path("ratings/<int:product_id>/", ProductRatingsAPI.as_view()),
    path("avg-rating/<int:product_id>/", ProductAverageAPI.as_view()),
    path("product-images/", ProductImageAPI.as_view()),
    path("product-images/<int:pk>/", ProductImageRUDAPI.as_view()),
    path("product/<int:product_id>/images/", ProductWiseImageAPI.as_view()),

    path("product-likes/",ProductLikeListCreateApiview.as_view(),name="product-like-list-create"),
    path("product-likes/<int:pk>/",ProductLikeDetailAPIView.as_view(),name="product-like-detail"),

    path("ai-photo/",AI_ShoeFinderView.as_view(),name="ai-photo-scan")
]