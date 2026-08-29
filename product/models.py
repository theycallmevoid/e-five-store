from django.db import models


class Product(models.Model):
    slug = models.SlugField(unique=True)
    sku = models.CharField(max_length=100, unique=True)
    price = models.PositiveIntegerField(help_text="Price in DZD")
    original_price = models.PositiveIntegerField(blank=True, null=True)
    badge = models.CharField(max_length=40, blank=True)
    name_en = models.CharField(max_length=150); name_fr = models.CharField(max_length=150, blank=True); name_ar = models.CharField(max_length=150, blank=True)
    subtitle_en = models.CharField(max_length=200); subtitle_fr = models.CharField(max_length=200, blank=True); subtitle_ar = models.CharField(max_length=200, blank=True)
    description_en = models.TextField(); description_fr = models.TextField(blank=True); description_ar = models.TextField(blank=True)
    benefits_en = models.TextField(help_text="One benefit per line"); benefits_fr = models.TextField(blank=True); benefits_ar = models.TextField(blank=True)
    usage_en = models.TextField(); usage_fr = models.TextField(blank=True); usage_ar = models.TextField(blank=True)
    main_image = models.ImageField(upload_to="products/")
    zr_product_id = models.UUIDField(blank=True, null=True, help_text="Product ID from the ZR Express catalog")
    length = models.PositiveSmallIntegerField(default=10, help_text="Centimetres")
    width = models.PositiveSmallIntegerField(default=10, help_text="Centimetres")
    height = models.PositiveSmallIntegerField(default=10, help_text="Centimetres")
    weight = models.DecimalField(max_digits=6, decimal_places=2, default=0.20, help_text="Kilograms")
    is_active = models.BooleanField(default=True); featured = models.BooleanField(default=False); sort_order = models.PositiveSmallIntegerField(default=0)
    class Meta: ordering = ("sort_order", "name_en")
    def __str__(self): return self.name_en


class ProductImage(models.Model):
    product = models.ForeignKey(Product, related_name="images", on_delete=models.CASCADE)
    image = models.ImageField(upload_to="products/gallery/")
    alt_text = models.CharField(max_length=160, blank=True)
    sort_order = models.PositiveSmallIntegerField(default=0)
    class Meta: ordering = ("sort_order", "id")
