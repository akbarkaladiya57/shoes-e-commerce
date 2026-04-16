from rest_framework.routers import DefaultRouter
from order_app.views import AddressAPI, OrderItemAPI

router = DefaultRouter()
router.register(r'addresses', AddressAPI, basename='addresses')
router.register(r'order-items',OrderItemAPI,basename='order-items')

urlpatterns = router.urls