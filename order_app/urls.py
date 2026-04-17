from rest_framework.routers import DefaultRouter
from order_app.views import AddressAPI, OrderItemAPI
from django.urls import path
from order_app.views import OrderAPI

router = DefaultRouter()
router.register(r'address', AddressAPI, basename='addresses')
router.register(r'order-items',OrderItemAPI,basename='order-items')

urlpatterns = [
    path('order/create/', OrderAPI.as_view(), name='order-list-create'),
]

urlpatterns += router.urls