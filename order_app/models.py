from datetime import timedelta

from django.db import models

from cart_app.models import PromoCode
from product_app.models import Product, TimeStamp
from user_app.models import User


# Create your models here


class Address(TimeStamp):
    ADDRESS_TYPE_CHOICE = (
        ("Home", "Home"),
        ("Office", "Office")
    )
    user = models.ForeignKey(User,on_delete=models.CASCADE,related_name="address")
    street = models.TextField()
    area = models.TextField()
    society_name = models.TextField()
    landmark = models.TextField()
    city = models.CharField(max_length=50)
    state = models.CharField(max_length=50)
    pincode = models.CharField(max_length=6)
    location = models.TextField()
    address_type = models.CharField(max_length=7,default="Home",choices=ADDRESS_TYPE_CHOICE)

    def __str__(self):
        return f"name :{self.user.username} | city :{self.city}"

class OrderItem(TimeStamp):
    user = models.ForeignKey(User,on_delete=models.CASCADE,related_name="items")
    quantity = models.PositiveIntegerField()
    product = models.ForeignKey(Product,on_delete=models.CASCADE,related_name="order_items")
    order = models.ForeignKey("Order",on_delete=models.CASCADE,related_name="items",null=True,blank=True)

    def __str__(self):
        return f"name :{self.user.username} | quantity :{self.quantity}"


class Order(TimeStamp):
    PAYMENT_CHOICES = (('credit cart' ,'Credit Cart'),('UPI','UPI'),('Net Banking','Net Banking'),('Cash on delivery','Cash On Delivery'))
    user = models.ForeignKey(User,on_delete=models.CASCADE,related_name="orders",null=True, blank=True)
    address = models.ForeignKey(Address,on_delete=models.CASCADE,related_name="orders")
    total_amount = models.DecimalField(max_digits=10,decimal_places=2)
    payment_method = models.CharField(max_length=50,choices=PAYMENT_CHOICES,default="UPI")
    status = models.CharField(max_length=50,default="pending")
    discount = models.DecimalField(max_digits=10,decimal_places=2,default=0)
    promo_code = models.ForeignKey(PromoCode,on_delete=models.SET_NULL,null=True,blank=True,related_name="codes")
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0)


    def __str__(self):
        return f"name :{self.discount} | total amount :{self.total_amount}"

    @property
    def delivery_date_formatted(self):
        return (self.created_at + timedelta(days=3)).strftime("%d %B %Y")
