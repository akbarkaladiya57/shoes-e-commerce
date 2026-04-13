from django.shortcuts import render
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.status import HTTP_400_BAD_REQUEST, HTTP_201_CREATED, HTTP_200_OK

from user_app.models import User, OtpVerification
from user_app.serializers import RegisterSerializer, LoginSerializer, ForgotPasswordSerializer,VerifyOtpSerializer, ResetPasswordSerializer


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



class SendOtpForForgotPassAPI(GenericAPIView):
    serializer_class = ForgotPasswordSerializer
    permission_classes = [AllowAny]

    def post(self,request):
        serializer = ForgotPasswordSerializer(data= request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data["email"]
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({"message": "invalid Email."},status=HTTP_400_BAD_REQUEST)

        otp_code = str(random.randint(1000,9999))

        OtpVerification.objects.create(user=user, otp=otp_code)

        return Response({
            "status": True,
            "message": "otp sent successfully",
            "otp-code": otp_code
        }, status=HTTP_200_OK)


class VerifyForgotPasswordOtpAPI(GenericAPIView):
    serializer_class = VerifyOtpSerializer
    permission_classes = [AllowAny]
    def post(self,request):
        serializer = VerifyOtpSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data.get("email")
        otp = serializer.validated_data.get("otp")

        try:
            user = User.objects.get(email=email)

            otp_object = OtpVerification.objects.filter(user=user, otp=otp, is_verified=False).latest("created_at")

        except User.DoesNotExist:
            return Response(
                {"status": False, "message": "User not found."},
                status=HTTP_400_BAD_REQUEST
            )

        except OtpVerification.DoesNotExist:
            return Response(
                {"status" : False, "message" : "Invalid OTP."},
                status= HTTP_400_BAD_REQUEST
            )

        if otp_object.is_expired:
            return Response({
                "status": False, "message": " OTP expired."
            }, status=HTTP_400_BAD_REQUEST)

        otp_object.is_verified = True
        otp_object.save()


        return Response({
            "status": True,
            "message": "OTP verified successfully."
        }, status=HTTP_200_OK)



class ResetPasswordAPI(GenericAPIView):
    serializer_class = ResetPasswordSerializer
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data["user"]
        otp_obj = serializer.validated_data["otp_obj"]
        new_password = serializer.validated_data["new_password"]

        user.set_password(new_password)
        user.save()


        otp_obj.is_used = True
        otp_obj.save()

        return Response({
            "status": True,
            "message": "Password reset successfully."
        }, status=HTTP_200_OK)