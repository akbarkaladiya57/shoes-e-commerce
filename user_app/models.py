from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.db import models
from django.utils import timezone
from user_app.manager import UserManager

# Create your models here.

class User(AbstractBaseUser, PermissionsMixin):
    GENDER_CHOICES = (("Male", "Male"), ("Female", "Female"), ("Other", "Other"))
    username = models.CharField(max_length=120)
    email = models.EmailField(unique=True)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, default="Male")
    date_of_birth = models.DateField()
    mobile_no = models.CharField(max_length=15)

    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    objects= UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS =["username","gender", "date_of_birth", "mobile_no"]

    def __str__(self):
        return f"email : {self.email} | name : {self.username} | phone_number : {self.mobile_no}"


class OtpVerification(models.Model):


    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="otps")
    otp = models.CharField(max_length=4)
    is_verified = models.BooleanField(default=False)
    is_used = models.BooleanField(default=False)
    expires_at = models.DateTimeField()
    created_at = models.DateTimeField(default=timezone.now)

    @property
    def is_expired(self):
        return timezone.now() > self.expires_at

    def __str__(self):
        return f"{self.user.email} - {self.otp}"