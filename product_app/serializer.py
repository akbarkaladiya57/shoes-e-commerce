from rest_framework import serializers
from product_app.models import Category, Product, Rating, ProductImage, ProductLike


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id","name","image","color"]


class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ["id", "image", "product"]


class ProductSerializer(serializers.ModelSerializer):
    product_images = ProductImageSerializer(many=True, read_only=True, source="images")

    images = serializers.ListField(
        child=serializers.ImageField(),
        write_only=True,
        required=False
    )

    class Meta:
        model = Product
        fields = [
            "id", "name", "brand", "price", "description",
            "is_male", "is_female", "is_child",
            "category", "size", "color","trending","special_shoes",
            "images",  # write
            "product_images"  # read
        ]

    def create(self, validated_data):
        images = validated_data.pop("images", [])
        product = Product.objects.create(**validated_data)

        for image in images:
            ProductImage.objects.create(product=product, image=image)

        return product

class ProductRUDSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ["id", "name", "brand", "price", "description", "is_male", "is_female", "is_child", "category", "size",
                  "color"]
        read_only_fields = ["id","name"]

class ProductCardSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()
    rating = serializers.SerializerMethodField()
    is_liked = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = ["id","name","brand","price","image","rating","is_liked","color"]

    def get_image(self, obj):
        first_image = obj.images.first()
        if first_image:
            request = self.context.get("request")
            return request.build_absolute_uri(first_image.image.url)
        return None

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

