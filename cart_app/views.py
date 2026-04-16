from django.shortcuts import render

# Create your views here.
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.status import HTTP_200_OK, HTTP_201_CREATED, HTTP_202_ACCEPTED, HTTP_204_NO_CONTENT, \
    HTTP_400_BAD_REQUEST
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

        return Response({"status" : True,"message": "Item added to cart"},status=HTTP_201_CREATED)


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
            "status" : True,
            "cart_id": cart.id,
            "items": serializer.data,
            "total price" : total_price
        },status=HTTP_200_OK)


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

        return Response({"status" : True,"message": "Quantity updated"},status=HTTP_202_ACCEPTED)


class RemoveCartItemAPI(GenericAPIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, item_id):
        try:
            item = CartItem.objects.get(id=item_id, cart__user=request.user)
        except CartItem.DoesNotExist:
            return Response({"status" : False,"error": "Item not found"}, status=HTTP_400_BAD_REQUEST)

        item.delete()

        return Response({"status" : True,"message": "Item removed"},status=HTTP_204_NO_CONTENT)


class ApplyPromoAPI(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        code = request.data.get("code")

        try:
            promo = PromoCode.objects.get(name=code)
        except PromoCode.DoesNotExist:
            return Response({"status" : False,"error": "Invalid promo code"}, status=HTTP_400_BAD_REQUEST)

        cart = Cart.objects.filter(user=request.user).first()

        if not cart:
            return Response({"status" : False,"error": "Cart is empty"}, status=HTTP_400_BAD_REQUEST)

        items = CartItem.objects.filter(cart=cart)

        total = sum([item.product.price * item.quantity for item in items])

        if promo.type == "flat":
            discount = promo.value
        elif promo.type == "percent":
            discount = (promo.value / 100) * total
        else:
            discount = 0

        final_price = max(total - discount,
                          )

        return Response({
            "status" : True,
            "total": total,
            "discount": discount,
            "final_price": final_price
        },status=HTTP_201_CREATED)