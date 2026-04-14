from rest_framework.generics import ListCreateAPIView, RetrieveUpdateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.permissions import IsAdminUser, AllowAny
from rest_framework.response import Response
from rest_framework.status import HTTP_204_NO_CONTENT

from product_app.models import Category, Product
from product_app.permission import AdminOrReadOnly
from product_app.serializer import CategorySerializer, ProductSerializer, ProductRUDSerializer


# Create your views here.
class CategoryAPI(ListCreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [AdminOrReadOnly]


class ProductCreateAPI(ListCreateAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [AdminOrReadOnly]


class ProductRetrieveUpdateAPI(RetrieveUpdateDestroyAPIView):
    serializer_class = ProductRUDSerializer
    permission_classes = [AdminOrReadOnly]

    def get_queryset(self):
        return Product.objects.filter(is_delete=False)

    def perform_destroy(self, instance):
        instance.is_deleted=True
        instance.save()

    def delete(self, request, *args, **kwargs):
        self.perform_destroy(self.get_object())
        return Response({"message" : "product soft delete successfully"},status=HTTP_204_NO_CONTENT)