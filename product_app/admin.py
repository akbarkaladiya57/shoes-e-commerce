from django.contrib import admin

from product_app.models import Product, ProductImage, Category, Rating, AvgRate, ProductLike


# Register your models here.
@admin.register(Product)
class AdminProduct(admin.ModelAdmin):
    list_display = ["id","name","brand","price","description","is_male","is_female","is_child","category","size","color","trending","special_shoes"]

@admin.register(ProductImage)
class AdminProductImage(admin.ModelAdmin):
    list_display = ["id","image","product","image_color"]

@admin.register(Category)
class AdminCategory(admin.ModelAdmin):
    list_display = ["id","name","color","image"]

@admin.register(Rating)
class RatingAdmin(admin.ModelAdmin):
    list_display = ["id","product","rate"]

@admin.register(AvgRate)
class AvgRateAdmin(admin.ModelAdmin):
    list_display = ["id","rate","total_count","average_rating"]

@admin.register(ProductLike)
class ProductLikeAdmin(admin.ModelAdmin):
    list_display = ["id","user","product"]