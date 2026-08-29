import uuid
from django.db import models
from product.models import Product


class Order(models.Model):
    STATUS = [("pending", "Pending"), ("confirmed", "Confirmed"), ("shipped", "Shipped"), ("delivered", "Delivered"), ("cancelled", "Cancelled")]
    reference = models.CharField(max_length=20, unique=True, editable=False)
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    SYNC_STATUS = [("pending", "Pending"), ("synced", "Synced"), ("failed", "Failed")]
    full_name = models.CharField(max_length=100); phone = models.CharField(max_length=20)
    wilaya_id = models.UUIDField(blank=True, null=True); wilaya = models.CharField(max_length=100)
    commune_id = models.UUIDField(blank=True, null=True); commune = models.CharField(max_length=100)
    pickup_hub_id = models.UUIDField(blank=True, null=True); pickup_hub_name = models.CharField(max_length=150, blank=True)
    address = models.CharField(max_length=250)
    delivery_type = models.CharField(max_length=30, default="home")
    product_price = models.PositiveIntegerField(); delivery_price = models.PositiveIntegerField(default=0); total_price = models.PositiveIntegerField()
    status = models.CharField(max_length=20, choices=STATUS, default="pending")
    zr_sync_status = models.CharField(max_length=20, choices=SYNC_STATUS, default="pending")
    zr_parcel_id = models.UUIDField(blank=True, null=True)
    zr_error = models.TextField(blank=True)
    notes = models.TextField(blank=True); created_at = models.DateTimeField(auto_now_add=True)
    def save(self, *args, **kwargs):
        if not self.reference: self.reference = f"EF-{uuid.uuid4().hex[:8].upper()}"
        super().save(*args, **kwargs)
    def __str__(self): return f"{self.reference} — {self.full_name}"
