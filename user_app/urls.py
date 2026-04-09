from django.urls import path

from user_app.views import UserRegisterAPI, UserLoginAPI, SendOtpForForgotPassAPI, ResetPasswordAPI, \
        VerifyForgotPasswordOtpAPI
url_patterns = [
        path("user-register/", UserRegisterAPI.as_view(), name="Register-user"),
        path("user-login/",UserLoginAPI.as_view(), name="user-login"),
        path("otp-for-forgot-password/",SendOtpForForgotPassAPI.as_view(), name="Send-Otp-For-Forgot-Password"),
        path("verify-otp",VerifyForgotPasswordOtpAPI.as_view(),name="Verify-Forgot-Password-Otp"),
        path("reset-password",ResetPasswordAPI.as_view(),name="Reset-Password")

]
