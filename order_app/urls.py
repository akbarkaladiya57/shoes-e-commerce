from rest_framework.routers import DefaultRouter
from order_app.views import AddressAPI, OrderItemAPI
from order_app.views import OrderAPI

router = DefaultRouter()
router.register(r'address', AddressAPI, basename='addresses')
router.register(r'order-items',OrderItemAPI,basename='order-items')
router.register(r'order-create',OrderAPI,basename='order-create')

urlpatterns = router.urls