from rest_framework import serializers
import ast
from cart_app.models import CartItem, PromoCode
from product_app.models import Product
from product_app.serializer import ProductImageSerializer


class AddToCartSerializer(serializers.Serializer):
    product = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all())
    quantity = serializers.IntegerField()
    size = serializers.CharField(required=False)
    color = serializers.CharField(required=False)


    def validate_quantity(self, value):
        if value <= 0:
            raise serializers.ValidationError("Quantity must be greater than 0")
        return value


class CartItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source="product.name")
    product_price = serializers.CharField(source="product.price")
    product_size = serializers.CharField(source="size")
    product_image = serializers.SerializerMethodField()
    product_color = serializers.CharField(source="color")

    class Meta:
        model = CartItem
        fields = ["id", "product", "product_name", "quantity","product_image","product_price","product_size","product_color"]

    def get_product_image(self, obj):
        request = self.context.get("request")

        image = obj.product.images.filter(image_color=obj.color).first()
        if image:
            url = image.image.url
            if request:
                url = request.build_absolute_uri(url)

            return url
        return None

class ApplyPromoSerializer(serializers.Serializer):
    cart_id = serializers.IntegerField()
    promo_code = serializers.CharField()
