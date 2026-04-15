from django.db.models import Avg, Count
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateAPIView, RetrieveUpdateDestroyAPIView, \
    GenericAPIView, ListAPIView
from rest_framework.permissions import IsAdminUser, AllowAny
from rest_framework.response import Response
from rest_framework.status import HTTP_204_NO_CONTENT
from rest_framework.views import APIView

from product_app.models import Category, Product, Rating, AvgRate
from product_app.permission import AdminOrReadOnly
from product_app.serializer import CategorySerializer, ProductSerializer, ProductRUDSerializer, RatingSerializer


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

class AddRatingAPI(GenericAPIView):
    serializer_class = RatingSerializer
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        product = serializer.validated_data["product"]
        rate_value = serializer.validated_data["rate"]

        rating = Rating.objects.create(
            product=product,
            rate=rate_value
        )

        ratings = Rating.objects.filter(product=product)

        avg_data = ratings.aggregate(
            avg_rating=Avg("rate"),
            total=Count("id")
        )

        avg_rating = avg_data["avg_rating"] or 0
        total_count = avg_data["total"]

        AvgRate.objects.create(
            rate=rating,
            average_rating=avg_rating,
            total_count=total_count
        )

        return Response({
            "message": "Rating added successfully",
            "average_rating": avg_rating,
            "total_count": total_count
        })


class ProductRatingsAPI(ListAPIView):
    serializer_class = RatingSerializer

    def get_queryset(self):
        product_id = self.kwargs["product_id"]
        return Rating.objects.filter(product_id=product_id)


class ProductAverageAPI(APIView):

    def get(self, request, product_id):
        ratings = Rating.objects.filter(product_id=product_id)

        if not ratings.exists():
            return Response({
                "average_rating": 0,
                "total_count": 0
            })

        avg_data = ratings.aggregate(
            avg_rating=Avg("rate"),
            total=Count("id")
        )

        return Response({
            "average_rating": avg_data["avg_rating"],
            "total_count": avg_data["total"]
        })