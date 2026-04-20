from rest_framework import serializers
from product_app.models import Category, Product, Rating, ProductImage


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id","name"]


class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ["id", "image"]


class ProductSerializer(serializers.ModelSerializer):
    images = ProductImageSerializer(many=True, required=False)

    class Meta:
        model = Product
        fields = [
            "id","name","brand","price","description",
            "is_male","is_female","is_child",
            "category","size","color","images"
        ]

    def create(self, validated_data):
        images_data = validated_data.pop("images", [])

        # create product
        product = Product.objects.create(**validated_data)

        # create images
        for image_data in images_data:
            ProductImage.objects.create(product=product, **image_data)

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