from django.contrib import admin

from product_app.models import Product, ProductImage, Category


# Register your models here.
@admin.register(Product)
class AdminProduct(admin.ModelAdmin):
    list_display = ["id","name","brand","price","description","is_male","is_female","is_child","category","size","color"]

@admin.register(ProductImage)
class AdminProductImage(admin.ModelAdmin):
    list_display = ["id","image","product"]

@admin.register(Category)
class AdminCategory(admin.ModelAdmin):
    list_display = ["id","name"]