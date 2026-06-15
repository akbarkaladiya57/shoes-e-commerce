from django.urls import path

from rest_framework.routers import DefaultRouter
from order_app.views import AddressAPI, OrderItemAPI, OrderListApiView, OrderDetailAPIView, BuyNowAPIView,ApplyPromoBuyNowAPIView
from order_app.views import OrderAPI

router = DefaultRouter()
router.register(r'address', AddressAPI, basename='addresses')
router.register(r'order-items',OrderItemAPI,basename='order-items')
router.register(r'order-create',OrderAPI,basename='order-create')

urlpatterns = router.urls + [
    path('my-orders/', OrderListApiView.as_view(), name='my-orders'),
    path("orders/<int:id>/", OrderDetailAPIView.as_view(), name="order-detail"),
    path("buy-now/",BuyNowAPIView.as_view(),name="buy-orders"),
    path("promo/apply/buy-now/",ApplyPromoBuyNowAPIView.as_view())
]