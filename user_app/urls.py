from django.urls import path

from user_app. views import UserRegisterAPI, UserLoginAPI
url_patterns = [
        path("user-register/", UserRegisterAPI.as_view(), name="Register-user"),
        path("user-login/",UserLoginAPI.as_view(), name="user-login"),
]





