from rest_framework import serializers

from cart_app.models import PromoCode
from order_app.models import Address, OrderItem, Order
from product_app.models import Product


class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = ["id", "user", "street", "area", "society_name","address_type","landmark", "city", "state", "pincode", "location",
                  "created_at", "updated_at"]
        read_only_fields = ["id", "user", "created_at", "updated_at"]


class OrderItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source="product.name")
    product_price = serializers.CharField(source="product.price")
    product_image = serializers.SerializerMethodField()
    gender = serializers.SerializerMethodField()
    discount_total = serializers.SerializerMethodField()
    line_total = serializers.SerializerMethodField()


    class Meta:
        model = OrderItem
        fields = ["id", "quantity", "product_name", "product_price", "product_image", "gender",
                  "line_total","discount_total"]

    def get_product_image(self, obj):
        request = self.context.get("request")

        image = obj.product.images.first()

        if image:
            url = image.image.url
            if request:
                url = request.build_absolute_uri(url)
            return url

        return None

    def get_gender(self, obj):
        product = obj.product

        if product.is_male:
            return "Male"
        elif product.is_female:
            return "Female"
        elif product.is_child:
            return "Child"

        return None

    def validate_quantity(self, value):
        if value < 0:
            raise serializers.ValidationError("quantity must be greater than 0")
        return value

    def get_discount_total(self, obj):
        order = obj.order

        subtotal = sum(
            item.product.price * item.quantity
            for item in order.items.all()
        )

        if not subtotal:
            return self.get_item_total(obj)

        order_discount = float(order.discount or 0)

        item_total = float(obj.product.price) * obj.quantity

        # proportional discount
        discount_share = (item_total / subtotal) * order_discount

        return round(item_total - discount_share, 2)

    def get_line_total(self, obj):
        return obj.quantity * obj.product.price


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    address = AddressSerializer(read_only=True)
    address_id = serializers.PrimaryKeyRelatedField(
        queryset=Address.objects.all(),
        source="address",
        write_only=True
    )
    promo_code_id = serializers.PrimaryKeyRelatedField(
        queryset=PromoCode.objects.all(),
        source="promo_code",
        write_only=True,
        required=False,
        allow_null=True
    )
    delivery_date = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = ["id", "user", "address", "total_amount", "payment_method", "status", "discount",
                  "items", "delivery_date","address_id","promo_code_id"]
        read_only_fields = ["id", "user", "created_at"]

    def get_delivery_date(self, obj):
        return obj.delivery_date_formatted

    def get_line_total(self, obj):
        return obj.quantity * obj.product.price


class OrderListSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(
        many=True,
        read_only=True
    )

    class Meta:
        model = Order
        fields = ["id", "created_at", "items"]


class OrderDetailSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    username = serializers.CharField(source="address.user.username", read_only=True)
    phone_number = serializers.CharField(source="address.user.mobile_no", read_only=True)
    address = AddressSerializer(read_only=True)
    product_price = serializers.SerializerMethodField()
    created_at = serializers.DateTimeField(read_only=True)
    delivery_date = serializers.SerializerMethodField()
    discount_amount = serializers.SerializerMethodField()




    class Meta:
        model = Order
        fields = ["id","items","username","phone_number","address","total_amount", "discount_amount",
                  "product_price", "created_at", "delivery_date"]

        read_only_fields = ["id", "total_amount", "discount", "created_at"]

    def get_product_price(self, obj):
        discount = obj.discount or 0
        return float(obj.total_amount) + float(discount)

    def get_discount_amount(self, obj):
        return float(obj.discount or 0)

    def get_delivery_date(self, obj):
        return obj.delivery_date_formatted

    def get_phone_number(self, obj):
        try:
            return obj.address.user.phone_number
        except AttributeError:
            return None

class BuyNowSerializer(serializers.Serializer):
    product_id = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all(),
        source="product"
    )
    quantity = serializers.IntegerField(min_value=1)
    address_id = serializers.PrimaryKeyRelatedField(
        queryset=Address.objects.all(),
        source="address"
    )
    payment_method = serializers.CharField()
    promo_code = serializers.PrimaryKeyRelatedField(
        queryset=PromoCode.objects.all(),
        required=False,
        allow_null=True
    )