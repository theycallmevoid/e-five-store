from django.contrib import admin
from .models import Order
from .services.zrexpress import sync_order


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("reference", "product", "full_name", "phone", "wilaya", "total_price", "status", "zr_sync_status", "created_at")
    list_filter = ("status", "zr_sync_status", "delivery_type", "wilaya")
    search_fields = ("reference", "full_name", "phone")
    readonly_fields = ("reference", "product_price", "total_price", "zr_parcel_id", "zr_error", "created_at")
    actions = ("retry_zr_synchronization",)

    @admin.action(description="Retry ZR Express synchronization")
    def retry_zr_synchronization(self, request, queryset):
        synced = sum(sync_order(order) for order in queryset)
        self.message_user(request, f"{synced} order(s) synchronized with ZR Express.")
