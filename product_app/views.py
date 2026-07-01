from django.db.models import Avg, Count
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView, \
    GenericAPIView, ListAPIView,RetrieveDestroyAPIView
from rest_framework.permissions import IsAdminUser, AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.status import HTTP_204_NO_CONTENT, HTTP_201_CREATED, HTTP_200_OK, HTTP_400_BAD_REQUEST, \
    HTTP_500_INTERNAL_SERVER_ERROR
from rest_framework.views import APIView


from product_app.models import Category, Product, Rating, AvgRate, ProductImage, ProductLike
from product_app.paginations import ProductPagination
# from product_app.paginations import ProductPagination
from product_app.permission import AdminOrReadOnly
from product_app.serializer import CategorySerializer, ProductSerializer, ProductRUDSerializer, RatingSerializer, \
    ProductImageSerializer, ProductLikeSerializer, ProductCardSerializer, ProductListSerializer, AIShoeFinderSerializer
from rest_framework.parsers import MultiPartParser, FormParser,JSONParser

# Create your views here.
class CategoryAPI(ListCreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [AdminOrReadOnly]
    parser_classes = [MultiPartParser, FormParser, JSONParser]


class ProductCreateAPI(ListCreateAPIView):
    queryset = Product.objects.all()
    permission_classes = [AdminOrReadOnly]

    def get_serializer_class(self):
        if self.request.method == "GET":
            return ProductListSerializer
        return ProductSerializer


    def perform_create(self, serializer):

        product = serializer.save()

        images = self.request.FILES.getlist("images")
        colors = self.request.data.getlist("image_color")

        for index, image in enumerate(images):
            color = colors[index] if index < len(colors) else ""

            ProductImage.objects.create(
                product=product,
                image=image,
                image_color=color
            )

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
        return Response({"status" : True,"message" : "product soft delete successfully"},status=HTTP_204_NO_CONTENT)

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
        },status=HTTP_201_CREATED)


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
            "status" : True,
            "average_rating": avg_data["avg_rating"],
            "total_count": avg_data["total"]
        },status=HTTP_200_OK)


class ProductImageAPI(ListCreateAPIView):
    queryset = ProductImage.objects.all()
    serializer_class = ProductImageSerializer
    permission_classes = [AdminOrReadOnly]


class ProductImageRUDAPI(RetrieveUpdateDestroyAPIView):
    queryset = ProductImage.objects.all()
    serializer_class = ProductImageSerializer
    permission_classes = [AdminOrReadOnly]


class ProductWiseImageAPI(ListAPIView):
    serializer_class = ProductImageSerializer

    def get_queryset(self):
        product_id = self.kwargs["product_id"]
        return ProductImage.objects.filter(product_id=product_id)


class CategoryFilterAPI(ListAPIView):
    queryset = Product.objects.all()
    permission_classes = [AllowAny]
    serializer_class = ProductCardSerializer
    # pagination_class = ProductPagination
    filter_backends = [DjangoFilterBackend]

    filterset_fields = ['category','is_male','is_female','is_child','trending','special_shoes']

    def get_queryset(self):
        queryset = Product.objects.filter(is_delete=False)
        return queryset


class ProductLikeListCreateApiview(ListCreateAPIView):
    serializer_class = ProductLikeSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return ProductLike.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class ProductLikeDetailAPIView(RetrieveDestroyAPIView):
    serializer_class = ProductLikeSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return ProductLike.objects.filter(user=self.request.user)



from .gemini_service import analyze_user_style
class AI_ShoeFinderView(APIView):

    def post(self, request):
        serializer = AIShoeFinderSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(
                serializer.errors,
                status=HTTP_400_BAD_REQUEST
            )

        validated_data = serializer.validated_data

        image = validated_data["image"]
        category_id = validated_data.get("category_id")
        size = validated_data.get("size")
        company_name = validated_data.get("company_name")

        # These will be applied AFTER AI recommendation
        min_price = validated_data.get("min_price")
        max_price = validated_data.get("max_price")

        try:
            image_bytes = image.read()

            # Initial filtering (before AI)
            products = Product.objects.filter(is_delete=False)

            if category_id:
                products = products.filter(category_id=category_id)

            if company_name:
                products = products.filter(
                    brand__icontains=company_name
                )

            if size:
                products = products.filter(
                    size__contains=[size]
                )

            products_data = list(
                products.values(
                    "id",
                    "name",
                    "description",
                    "price",
                    "is_male",
                    "is_female",
                    "is_child",
                    "trending",
                    "special_shoes",
                    "category__name",
                )
            )

            ai_result = analyze_user_style(
                image_bytes=image_bytes,
                products=products_data
            )

            if not ai_result:
                return Response(
                    {
                        "success": False,
                        "error": "Gemini failed"
                    },
                    status=HTTP_500_INTERNAL_SERVER_ERROR
                )

            # AI recommended products
            recommended_products = Product.objects.filter(
                id__in=ai_result.product_ids,
                is_delete=False
            )

            # Apply price filters AFTER AI
            if min_price is not None:
                recommended_products = recommended_products.filter(
                    price__gte=min_price
                )

            if max_price is not None:
                recommended_products = recommended_products.filter(
                    price__lte=max_price
                )

            response_serializer = ProductCardSerializer(
                recommended_products,
                many=True,
                context={"request": request}
            )

            return Response(
                {
                    "success": True,
                    "image_summary": ai_result.image_summary,
                    "recommendation_reason": ai_result.recommendation_reason,
                    "recommended_products": response_serializer.data,
                }
            )

        except Exception as e:
            return Response(
                {
                    "success": False,
                    "error": str(e)
                },
                status=HTTP_500_INTERNAL_SERVER_ERROR
            )