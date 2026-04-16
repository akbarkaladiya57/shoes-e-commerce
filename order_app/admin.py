from django.contrib import admin

from order_app.models import Address, OrderItem, Order


# Register your models here.
@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ["id","user","street","area","society_name","landmark","city","state","pincode","location"]

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ["id","user","quantity","product"]

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ["id","address","total_amount","payment_method","status","discount","promo_code","order_items"]
