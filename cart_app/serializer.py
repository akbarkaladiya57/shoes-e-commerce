from rest_framework import serializers

from cart_app.models import CartItem
from product_app.models import Product


class AddToCartSerializer(serializers.Serializer):
    product = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all())
    quantity = serializers.IntegerField()

    def validate_quantity(self, value):
        if value <= 0:
            raise serializers.ValidationError("Quantity must be greater than 0")
        return value


class CartItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source="product.name")

    class Meta:
        model = CartItem
        fields = ["id", "product", "product_name", "quantity"]


