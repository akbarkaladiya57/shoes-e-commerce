from django.contrib import admin

from cart_app.models import PromoCode


# Register your models here.
@admin.register(PromoCode)
class PromoCodeAdmin(admin.ModelAdmin):
    list_display = ["id", "name", "value", "type"]