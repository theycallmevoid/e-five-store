from django.contrib import admin
from .models import Product, ProductImage


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name_en", "price", "is_active", "featured", "sort_order")
    list_editable = ("price", "is_active", "featured", "sort_order")
    search_fields = ("name_en", "name_fr", "name_ar", "sku")
    prepopulated_fields = {"slug": ("name_en",)}
    inlines = [ProductImageInline]
    fieldsets = (("Store", {"fields": ("slug", "sku", "price", "original_price", "badge", "main_image", "is_active", "featured", "sort_order")}), ("English", {"fields": ("name_en", "subtitle_en", "description_en", "benefits_en", "usage_en")}), ("French", {"fields": ("name_fr", "subtitle_fr", "description_fr", "benefits_fr", "usage_fr")}), ("Arabic", {"fields": ("name_ar", "subtitle_ar", "description_ar", "benefits_ar", "usage_ar")}), ("ZR Express", {"fields": ("zr_product_id", "length", "width", "height", "weight")}))
