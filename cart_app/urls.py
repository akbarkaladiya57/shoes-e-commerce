from django.urls import path

from cart_app.views import AddToCartAPI, CartDetailAPI, UpdateCartItemAPI, RemoveCartItemAPI, ApplyPromoAPI, \
    CheckPromoCode

cart_urlpatterns = [
    path("cart/add/", AddToCartAPI.as_view()),
    path("cart/", CartDetailAPI.as_view()),
    path("cart/update/<int:item_id>/", UpdateCartItemAPI.as_view()),
    path("cart/remove/<int:item_id>/", RemoveCartItemAPI.as_view()),
    path("cart/apply-promo/", ApplyPromoAPI.as_view()),
    path("cart/check-promo/", CheckPromoCode.as_view()),
]