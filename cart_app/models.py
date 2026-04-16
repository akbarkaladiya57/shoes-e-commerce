from django.db import models

from product_app.models import Product
from user_app.models import User


# Create your models here.
class TimeStamp(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

class Cart(TimeStamp):
    user = models.ForeignKey(User,on_delete=models.CASCADE,related_name="carts")

class CartItem(TimeStamp):
    cart = models.ForeignKey(Cart,on_delete=models.CASCADE,related_name="items")
    product = models.ForeignKey(Product,on_delete=models.CASCADE,related_name="items")
    quantity = models.PositiveIntegerField()

    def __str__(self):
        return f"product : {self.product.name} | quantity : {self.quantity}"


class PromoCode(TimeStamp):
    TYPE_CHOICE = (
        ("flat","flat"),
        ("percentage","percentage")
    )
    name = models.CharField(max_length=250)
    value = models.PositiveIntegerField()
    type = models.CharField(max_length=50,choices=TYPE_CHOICE)

    def __str__(self):
        return f"name : {self.name} | value :{self.value}"