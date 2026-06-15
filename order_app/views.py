from decimal import Decimal

from django.db import transaction
from rest_framework import viewsets
from rest_framework.generics import ListCreateAPIView, ListAPIView, RetrieveAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_201_CREATED, HTTP_400_BAD_REQUEST, HTTP_404_NOT_FOUND
from rest_framework.views import APIView

from cart_app.models import Cart, CartItem, PromoCode
from order_app.models import Address, OrderItem, Order
from order_app.serializer import AddressSerializer, OrderItemSerializer, OrderSerializer, OrderListSerializer, \
    OrderDetailSerializer, BuyNowSerializer, ApplyPromoBuyNowSerializer


# Create your views here.
class AddressAPI(viewsets.ModelViewSet):
    serializer_class = AddressSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Address.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()

        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        serializer.save(user=request.user)

        return Response({
            "success": True,
            "message": "Address updated successfully",
            "data": serializer.data
        }, status=HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)

        return Response({
            "success": True,
            "message": "Address deleted successfully"
        }, status=HTTP_200_OK)

class OrderItemAPI(viewsets.ModelViewSet):
    serializer_class = OrderItemSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return OrderItem.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)

        return Response({
            "status": True,
            "message": "Item added successfully",
            "data": response.data
        }, status=HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        response = super().update(request, *args, **kwargs)

        return Response({
            "success": True,
            "message": "Item updated successfully",
            "data": response.data
        }, status=HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)

        return Response({
            "success": True,
            "message": "Item deleted successfully"
        }, status=HTTP_200_OK)



class OrderAPI(viewsets.ModelViewSet):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        print(self.request.user)
        return Order.objects.filter(user=self.request.user).prefetch_related("items__product__images")

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    # def create(self, request, *args, **kwargs):
    #     serializer = self.get_serializer(data=request.data)
    #     serializer.is_valid(raise_exception=True)
    #     self.perform_create(serializer)
    #
    #     return Response({
    #         "success": True,
    #         "message": "Order created successfully",
    #         "data": serializer.data
    #     }, status=HTTP_201_CREATED)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)

        return Response({
            "success": True,
            "data": serializer.data
        }, status=HTTP_200_OK)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()

        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response({
            "success": True,
            "message": "Order updated successfully",
            "data": serializer.data
        }, status=HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)

        return Response({
            "success": True,
            "message": "Order deleted successfully"
        }, status=HTTP_200_OK)

    def create(self, request, *args, **kwargs):
        print(request.data)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = request.user

        cart = Cart.objects.filter(user=user).first()

        if not cart:
            return Response({
                "success": False,
                "message": "Cart is empty"
            }, status=400)

        cart_items = CartItem.objects.filter(cart=cart)

        if not cart_items.exists():
            return Response({
                "success": False,
                "message": "No items in cart"
            }, status=400)

        subtotal = sum(
            item.product.price * item.quantity
            for item in cart_items
        )
        print("SUBTOTAL:", subtotal)

        print(serializer.validated_data)
        promo_code = serializer.validated_data.get("promo_code")
        print("PROMO CODE RAW:", promo_code)
        discount = Decimal("0.00")

        if promo_code:
            if promo_code.type == "flat":
                discount = Decimal(str(promo_code.value))

            elif promo_code.type == "percentage":
                discount = (Decimal(str(subtotal))* Decimal(str(promo_code.value))) / Decimal("100")

        print("DISCOUNT CALCULATED:", discount)
        final_amount = Decimal(str(subtotal)) - discount
        print("FINAL AMOUNT BEFORE FIX:", final_amount)

        if final_amount < 0:
            final_amount = Decimal("0.00")

        print("FINAL AMOUNT FINAL:", final_amount)

        with transaction.atomic():

            order = serializer.save(
                user=user,
                subtotal=subtotal,
                total_amount=final_amount,
                discount=discount
            )

            OrderItem.objects.bulk_create([
                OrderItem(
                    user=user,
                    product=item.product,
                    quantity=item.quantity,
                    order=order
                )
                for item in cart_items
            ])

            cart_items.delete()

        return Response({
            "success": True,
            "message": "Order created successfully from cart",
            "data": OrderSerializer(order).data
        }, status=201)

class OrderListApiView(ListAPIView):
    serializer_class = OrderListSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).order_by("-created_at")

class OrderDetailAPIView(RetrieveAPIView):
    serializer_class = OrderDetailSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = "id"

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)

class BuyNowAPIView(APIView):

    def post(self, request):
        serializer = BuyNowSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = request.user

        product = serializer.validated_data["product"]
        quantity = serializer.validated_data["quantity"]
        address = serializer.validated_data["address"]
        payment_method = serializer.validated_data["payment_method"]
        promo_code = serializer.validated_data.get("promo_code")

        total_amount = Decimal(str(product.price)) * quantity

        discount = Decimal("0.00")

        if promo_code:
            if promo_code.type == "flat":
                discount = Decimal(str(promo_code.value))

            elif promo_code.type == "percentage":
                discount = (
                    total_amount * Decimal(str(promo_code.value))
                ) / Decimal("100")

        final_amount = total_amount - discount

        if final_amount < 0:
            final_amount = Decimal("0.00")

        with transaction.atomic():

            order = Order.objects.create(
                user=user,
                address=address,
                payment_method=payment_method,
                total_amount=final_amount,
                discount=discount,
            )

            OrderItem.objects.create(
                user=user,
                order=order,
                product=product,
                quantity=quantity,
            )

        return Response({
            "success": True,
            "message": "Order created successfully",
            "data": OrderSerializer(order).data
        }, status=201)

def calculate_discount(amount, promo):
    """
    Centralized discount logic for reuse across views.
    """
    promo_type = promo.type.lower()

    if promo_type == "flat":
        return min(promo.value, amount)

    if promo_type == "percentage":
        return (amount * promo.value) / 100

    return 0


class ApplyPromoBuyNowAPIView(APIView):

    def post(self, request):
        serializer = ApplyPromoBuyNowSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)

        product = serializer.validated_data["product"]
        promo = serializer.validated_data["promo_code"]

        product_price = product.price

        # calculate discount safely
        discount = calculate_discount(product_price, promo)
        final_total = max(product_price - discount, 0)

        return Response(
            {
                "promo_id": promo.id,
                "promo_name": promo.name,
                "promo_code": promo.name,  # fixed (was promo.codes in your code)
                "product_id": product.id,
                "product_price": product_price,
                "discount": discount,
                "final_total": final_total,
            },
            status=HTTP_200_OK
        )