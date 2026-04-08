from django.shortcuts import render
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.status import HTTP_400_BAD_REQUEST, HTTP_201_CREATED, HTTP_200_OK

from user_app.models import User
from user_app.serializers import RegisterSerializer, LoginSerializer


# Create your views here.


class UserRegisterAPI(GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = RegisterSerializer

    def post(self,request):
        serializer = RegisterSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({
                "data" :  None,
                "status" : False,
                "message" : "data not available.",
                "error" : serializer.errors
            },status=HTTP_400_BAD_REQUEST)
        serializer.save()
        return Response({
            "status" : True,
            "message" : "user registered successfully.",
            "data" : serializer.data
        },status=HTTP_201_CREATED)

    def get(self,request):
        user = User.objects.all()
        serializer = RegisterSerializer(user, many=True)
        return Response({
            "status" : True,
            "message" : "all users",
            "data" : serializer.data
        },status=HTTP_200_OK)


class UserLoginAPI(GenericAPIView):
    serializer_class = LoginSerializer
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data["email"]
        password = serializer.validated_data["password"]

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({"message" : "Invalid credentials"},status=HTTP_400_BAD_REQUEST)

        if not user.check_password(password):
            return Response({"message": "Invalid credentials"},status=HTTP_400_BAD_REQUEST)

        return Response({
            "status" : True,
            "message" : "user logged in successfully "
        },status=HTTP_200_OK)




