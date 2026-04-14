from rest_framework.generics import ListCreateAPIView
from rest_framework.permissions import IsAdminUser, AllowAny

from product_app.models import Category, Product
from product_app.permission import AdminOrReadOnly
from product_app.serializer import CategorySerializer, ProductSerializer


# Create your views here.
class CategoryAPI(ListCreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [AdminOrReadOnly]


class ProductCreateAPI(ListCreateAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [AdminOrReadOnly]
