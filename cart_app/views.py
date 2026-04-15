from django.shortcuts import render

# Create your views here.
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from cart_app.models import Cart, CartItem, PromoCode
from cart_app.serializer import AddToCartSerializer, CartItemSerializer


class AddToCartAPI(GenericAPIView):
    serializer_class = AddToCartSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        product = serializer.validated_data["product"]
        quantity = serializer.validated_data["quantity"]

        # Get or create cart
        cart, _ = Cart.objects.get_or_create(user=user)

        # Add or update item
        item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
            defaults={"quantity": quantity}
        )

        if not created:
            item.quantity += quantity
            item.save()

        return Response({"message": "Item added to cart"})


class CartDetailAPI(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        cart = Cart.objects.filter(user=user).first()

        if not cart:
            return Response({"items": []})

        items = CartItem.objects.filter(cart=cart)
        serializer = CartItemSerializer(items, many=True)
        total_price = sum(item.product.price * item.quantity for item in items)

        return Response({
            "cart_id": cart.id,
            "items": serializer.data,
            "total price" : total_price
        })


class UpdateCartItemAPI(GenericAPIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, item_id):
        try:
            item = CartItem.objects.get(id=item_id, cart__user=request.user)
        except CartItem.DoesNotExist:
            return Response({"error": "Item not found"}, status=404)

        quantity = request.data.get("quantity")

        if not quantity or int(quantity) <= 0:
            return Response({"error": "Invalid quantity"}, status=400)

        item.quantity = int(quantity)
        item.save()

        return Response({"message": "Quantity updated"})


class RemoveCartItemAPI(GenericAPIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, item_id):
        try:
            item = CartItem.objects.get(id=item_id, cart__user=request.user)
        except CartItem.DoesNotExist:
            return Response({"error": "Item not found"}, status=404)

        item.delete()

        return Response({"message": "Item removed"})


class ApplyPromoAPI(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        code = request.data.get("code")

        try:
            promo = PromoCode.objects.get(name=code)
        except PromoCode.DoesNotExist:
            return Response({"error": "Invalid promo code"}, status=400)

        cart = Cart.objects.filter(user=request.user).first()

        if not cart:
            return Response({"error": "Cart is empty"}, status=400)

        items = CartItem.objects.filter(cart=cart)

        total = sum([item.product.price * item.quantity for item in items])

        if promo.type == "flat":
            discount = promo.value
        elif promo.type == "percent":
            discount = (promo.value / 100) * total
        else:
            discount = 0

        final_price = max(total - discount, 0)

        return Response({
            "total": total,
            "discount": discount,
            "final_price": final_price
        })