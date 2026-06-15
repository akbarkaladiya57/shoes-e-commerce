from django.db.models import Avg
from rest_framework import serializers
from product_app.models import Category, Product, Rating, ProductImage, ProductLike


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id","name","image","color"]


class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ["image", "image_color"]


class ProductImageCreateSerializer(serializers.Serializer):
    image = serializers.ImageField()
    image_color = serializers.CharField(
        max_length=7,
        required=False,
        allow_null=True,
        allow_blank=True
    )



class ProductSerializer(serializers.ModelSerializer):
    images = ProductImageCreateSerializer(
        many=True,
        write_only=True,
        required=False
    )

    class Meta:
        model = Product
        fields = [
            "id", "name", "brand", "price",
            "is_male", "is_female", "is_child","size",
            "category", "color",
            "images",
            "trending","special_shoes"# read
        ]


    def create(self, validated_data):
        validated_data.pop("images", [])
        product = Product.objects.create(**validated_data)

        return product


class ProductListSerializer(serializers.ModelSerializer):
    product_image = serializers.SerializerMethodField()
    is_liked = serializers.SerializerMethodField()
    rating = serializers.SerializerMethodField()


    class Meta:
        model = Product
        fields = ["id", "is_liked","trending","special_shoes","name", "brand", "price", "category", "color",
            "is_male", "is_female", "is_child", "product_image","rating"]


    def get_is_liked(self, obj):
        request = self.context.get("request")

        if request and request.user.is_authenticated:
            return ProductLike.objects.filter(
                user=request.user,
                product=obj
            ).exists()

        return False

    def get_rating(self, obj):
        ratings = Rating.objects.filter(product=obj)

        if ratings.exists():
            avg_rating = ratings.aggregate(avg=Avg("rate"))["avg"]
            return round(avg_rating, 1)

        return 0

    def get_product_image(self, obj):
        request = self.context.get("request")

        image = obj.images.first()
        if image:
            url = image.image.url
            if request:
                url = request.build_absolute_uri(url)

            return url
        return None

class ProductRUDSerializer(serializers.ModelSerializer):
    product_images = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = ["id", "name", "brand", "price", "description", "is_male", "is_female", "is_child", "category", "size",
                  "color","product_images"]
        read_only_fields = ["id","name"]

    def get_product_images(self, obj):
        grouped = {}

        images = obj.images.all()  # related_name="images"

        for img in images:
            color = img.image_color or "unknown"

            if color not in grouped:
                grouped[color] = []

            request = self.context.get("request")
            url = img.image.url

            if request:
                url = request.build_absolute_uri(url)

            grouped[color].append(url)

        return grouped

class ProductCardSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()
    rating = serializers.SerializerMethodField()
    is_liked = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = ["id","name","brand","price","image","rating","is_liked","color"]

    def get_image(self, obj):
        first_image = obj.images.first()

        if not first_image:
            return None

        url = first_image.image.url
        request = self.context.get("request")

        if request:
            return request.build_absolute_uri(url)

        return url

    def get_rating(self, obj):
        ratings = Rating.objects.filter(product=obj)

        if ratings.exists():
            return round(
                sum(r.rate for r in ratings) / ratings.count(),
                1
            )

        return 0

    def get_is_liked(self, obj):
        request = self.context.get("request")

        if request and request.user.is_authenticated:
            return ProductLike.objects.filter(
                user=request.user,
                product=obj
            ).exists()

        return False

class RatingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rating
        fields = ["product", "rate"]

    def validate_rate(self, value):
        if value < 0 or value > 5:
            raise serializers.ValidationError("Rating must be between 0 and 5")
        return value


class ProductLikeSerializer(serializers.ModelSerializer):
    is_liked = serializers.SerializerMethodField()

    class Meta:
        model = ProductLike
        fields = ["id","user","product","is_liked"]
        read_only_fields = ["id","user"]

    def validate(self, attrs):
        user = self.context["request"].user
        product = attrs.get("product")

        if self.instance is None:
            if ProductLike.objects.filter(user=user,product=product).exists():
                raise serializers.ValidationError("You already liked this product.")
        return attrs

    def get_is_liked(self, obj):
        request = self.context.get("request")

        if request and request.user.is_authenticated:
            return ProductLike.objects.filter(
                user=request.user,
                product=obj.product
            ).exists()

        return False

class AIShoeFinderSerializer(serializers.Serializer):
    image = serializers.ImageField(required=True)
    category_id = serializers.IntegerField(required=False)
    size = serializers.CharField(required=False, allow_blank=True)
    company_name = serializers.CharField(required=False, allow_blank=True)

    min_price = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        required=False
    )

    max_price = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        required=False
    )

    def validate_image(self, value):
        allowed_extensions = ["jpg", "jpeg", "png", "webp"]

        ext = value.name.split(".")[-1].lower()

        if ext not in allowed_extensions:
            raise serializers.ValidationError(
                "Only JPG, JPEG, PNG and WEBP images are allowed."
            )

        if value.size > 5 * 1024 * 1024:
            raise serializers.ValidationError(
                "Image size cannot exceed 5MB."
            )

        return value

    def validate(self, attrs):
        price_min = attrs.get("price_min")
        price_max = attrs.get("price_max")

        if (
                price_min is not None and
                price_max is not None and
                price_min > price_max
        ):
            raise serializers.ValidationError(
                {
                    "price_max": "price_max must be greater than or equal to price_min."
                }
            )

        return attrs