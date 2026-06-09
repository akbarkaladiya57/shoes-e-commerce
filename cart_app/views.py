from django.shortcuts import render

# Create your views here.
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.status import HTTP_200_OK, HTTP_201_CREATED, HTTP_202_ACCEPTED, HTTP_204_NO_CONTENT, \
    HTTP_400_BAD_REQUEST, HTTP_404_NOT_FOUND
from rest_framework.views import APIView

from cart_app.models import Cart, CartItem, PromoCode
from cart_app.serializer import AddToCartSerializer, CartItemSerializer, ApplyPromoSerializer


class AddToCartAPI(GenericAPIView):
    serializer_class = AddToCartSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        product = serializer.validated_data["product"]
        quantity = serializer.validated_data["quantity"]
        size = serializer.validated_data.get("size")
        color = serializer.validated_data.get("color")

        # Get or create cart
        cart, _ = Cart.objects.get_or_create(user=user)

        # Add or update item
        item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
            size = size,
            color = color,
            defaults={"quantity": quantity}
        )

        if not created:
            item.quantity += quantity
            item.save()

        return Response({"status": True, "message": "Item added to cart"}, status=HTTP_201_CREATED)


class CartDetailAPI(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        cart = Cart.objects.filter(user=user).first()

        if not cart:
            return Response({"items": []})

        items = CartItem.objects.filter(cart=cart)
        serializer = CartItemSerializer(items, many=True,context={"request": request})
        total_price = sum(item.product.price * item.quantity for item in items)

        return Response({
            "status": True,
            "cart_id": cart.id,
            "items": serializer.data,
            "total price": total_price
        }, status=HTTP_200_OK)


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

        return Response({"status": True, "message": "Quantity updated"}, status=HTTP_202_ACCEPTED)


class RemoveCartItemAPI(GenericAPIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, item_id):
        try:
            item = CartItem.objects.get(id=item_id, cart__user=request.user)
        except CartItem.DoesNotExist:
            return Response({"status": False, "error": "Item not found"}, status=HTTP_400_BAD_REQUEST)

        item.delete()

        return Response({"status": True, "message": "Item removed"}, status=HTTP_204_NO_CONTENT)


class ApplyPromoAPI(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        code = request.query_params.get("code")

        try:
            promo = PromoCode.objects.get(name=code)
        except PromoCode.DoesNotExist:
            return Response({"status": False, "error": "Invalid promo code"}, status=HTTP_400_BAD_REQUEST)

        cart = Cart.objects.filter(user=request.user).first()

        if not cart:
            return Response({"status": False, "error": "Cart is empty"}, status=HTTP_400_BAD_REQUEST)

        items = CartItem.objects.filter(cart=cart)

        total = sum([item.product.price * item.quantity for item in items])

        if promo.type == "flat":
            discount = promo.value
        elif promo.type == "percent":
            discount = (promo.value / 100) * total
        else:
            discount = 0

        final_price = total - discount

        return Response({
            "status": True,
            "total": total,
            "discount": discount,
            "final_price": final_price
        }, status=HTTP_200_OK)



class CheckPromoCode(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        promo_code = request.query_params.get("promo_code")

        # Validate input
        if not promo_code:
            return Response(
                {"status": False, "error": "Promo code is required"},
                status=HTTP_400_BAD_REQUEST
            )

        # Check existence
        if PromoCode.objects.filter(name=promo_code).exists():
            return Response(
                {"status": True, "message": "Valid promo code"},
                status=HTTP_200_OK
            )
        else:
            return Response(
                {"status": False, "error": "Invalid promo code"},
                status=HTTP_400_BAD_REQUEST
            )


class ApplyPromoAPIView(APIView):

    def post(self, request):

        serializer = ApplyPromoSerializer(data=request.data)

        if serializer.is_valid():

            cart_id = serializer.validated_data["cart_id"]
            promo_name = serializer.validated_data["promo_code"]

            try:
                cart = Cart.objects.get(id=cart_id)
            except Cart.DoesNotExist:
                return Response(
                    {"error": "Cart not found"},
                    status=HTTP_404_NOT_FOUND
                )

            try:
                promo = PromoCode.objects.get(name=promo_name)
            except PromoCode.DoesNotExist:
                return Response(
                    {"error": "Invalid promo code"},
                    status=HTTP_404_NOT_FOUND
                )

            total = 0

            for item in cart.items.all():
                total += item.product.price * item.quantity

            discount = 0

            if promo.type == "flat":
                discount = promo.value

            elif promo.type == "percentage":
                discount = (total * promo.value) / 100

            final_total = total - discount

            if final_total < 0:
                final_total = 0

            return Response({
                "promo_id": promo.id,
                "cart_total": total,
                "discount": discount,
                "final_total": final_total,
                "promo_code": promo.name
            })

        return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)