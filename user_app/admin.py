from django.contrib import admin

from user_app.models import User


# Register your models here.
@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ["id","username","email","gender","date_of_birth","mobile_no"]