from rest_framework.generics import ListCreateAPIView
from rest_framework.permissions import IsAdminUser, AllowAny

from product_app.models import Category, Product
from product_app.serializer import CategorySerializer, ProductSerializer


# Create your views here.
class CategoryAPI(ListCreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

    def get_permissions(self):
        if self.request.method == "POST":
            return [IsAdminUser()]
        return [AllowAny()]

class ProductCreateAPI(ListCreateAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

    def get_permissions(self):
        if self.request.method == "POST":
            return [IsAdminUser()]
        return [AllowAny()]
