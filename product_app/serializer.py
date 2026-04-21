from rest_framework import serializers
from product_app.models import Category, Product, Rating, ProductImage


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id","name"]


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
            "category", "size", "color",
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


class RatingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rating
        fields = ["product", "rate"]

    def validate_rate(self, value):
        if value < 0 or value > 5:
            raise serializers.ValidationError("Rating must be between 0 and 5")
        return value