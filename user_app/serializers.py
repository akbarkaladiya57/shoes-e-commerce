from rest_framework import serializers

from user_app.models import User, OtpVerification


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    class Meta:
        model = User
        fields = ["id","username","email","password","gender","date_of_birth","mobile_no"]

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()


class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()



class VerifyOtpSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField(max_length=4)


class ResetPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()
    new_password = serializers.CharField(write_only=True)
    otp = serializers.CharField(max_length=4)

    def validate(self, attrs):
        email = attrs.get("email")
        otp = attrs.get("otp")

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError({
                "email": "User does not exist."
            })

        try:
            otp_obj = OtpVerification.objects.get(
                user=user,
                otp=otp,
                is_used=False
            )
        except OtpVerification.DoesNotExist:
            raise serializers.ValidationError({
                "otp": "Invalid OTP or OTP not verified."
            })

        attrs["user"] = user
        attrs["otp_obj"] = otp_obj

        return attrs


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id","username","email","gender","date_of_birth","mobile_no"]

class UpdatePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)