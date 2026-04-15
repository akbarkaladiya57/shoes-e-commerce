from django.db import models

# Create your models here.

class TimeStamp(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

class Product(TimeStamp):
    name = models.CharField(max_length=150)
    brand = models.CharField(max_length=150)
    price = models.PositiveIntegerField()
    description = models.TextField()
    is_male = models.BooleanField(default=True)
    is_female = models.BooleanField(default=False)
    is_child = models.BooleanField(default=False)
    category = models.ForeignKey("Category",on_delete=models.CASCADE,related_name="products")
    size = models.JSONField(default=list,blank=True)
    color = models.CharField(max_length=50)

    is_delete = models.BooleanField(default=False)

    def __str__(self):
        return f"name : {self.name} | brand :{self.brand} | category : {self.category}"

class ProductImage(TimeStamp):
    image = models.ImageField(upload_to="media/products")
    product = models.ForeignKey(Product,on_delete=models.CASCADE,related_name="images")

class Category(TimeStamp):
    name = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.name} "


class Rating(TimeStamp):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="ratings")
    rate = models.DecimalField(max_digits=2, decimal_places=1)

    def __str__(self):
        return f"product : {self.product.name} | rate : {self.rate}"



class AvgRate(TimeStamp):
    rate = models.ForeignKey(Rating, on_delete=models.CASCADE, related_name="average_rate")
    total_count = models.DecimalField(max_digits=10, decimal_places=2)
    average_rating = models.DecimalField(max_digits=10, decimal_places=2)
