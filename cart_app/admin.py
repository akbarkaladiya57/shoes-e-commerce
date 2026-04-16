from django.contrib import admin

from cart_app.models import PromoCode, Cart, CartItem


# Register your models here.
@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ["id","user"]


@admin.register(PromoCode)
class PromoCodeAdmin(admin.ModelAdmin):
    list_display = ["id", "name", "value", "type"]

@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ["id","cart","product","quantity"]