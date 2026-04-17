from rest_framework import serializers

from order_app.models import Address, OrderItem, Order


class AddressSerializer(serializers.ModelSerializer):

    class Meta:
        model = Address
        fields = ["id","user","street","area","society_name","landmark","city","state","pincode","location","created_at","updated_at"]
        read_only_fields = ["id", "user","created_at","updated_at"]

class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ["id","user","quantity","product","order"]
        read_only_fields = ["id","user"]

    def validate_quantity(self,value):
        if value < 0:
            raise serializers.ValidationError("quantity must be greater than 0")
        return value

class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ["id","address","total_amount","payment_method","status","discount","promo_code"]
