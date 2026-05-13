from django.contrib import admin

from user_app.models import User, OtpVerification


# Register your models here.
@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ["id","username","email","gender","date_of_birth","mobile_no"]


@admin.register(OtpVerification)
class OtpVerificationAdmin(admin.ModelAdmin):
    list_display = ["user","otp", "is_verified", "is_used"]