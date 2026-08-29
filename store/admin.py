from django.contrib import admin
from .models import StoreSettings, TrackingPixelSettings, ZRExpressSettings


@admin.register(StoreSettings)
class StoreSettingsAdmin(admin.ModelAdmin):
    def has_add_permission(self, request): return not StoreSettings.objects.exists()
    def has_delete_permission(self, request, obj=None): return False


@admin.register(ZRExpressSettings)
class ZRExpressSettingsAdmin(admin.ModelAdmin):
    fieldsets = (("Connection", {"fields": ("api_base", "tenant_id", "secret_key", "live_sync"), "description": "Credentials are stored in the Django database and are never read from environment variables."}),)
    def has_add_permission(self, request): return not ZRExpressSettings.objects.exists()
    def has_delete_permission(self, request, obj=None): return False


@admin.register(TrackingPixelSettings)
class TrackingPixelSettingsAdmin(admin.ModelAdmin):
    fieldsets = (
        ("Status", {"fields": ("enabled",)}),
        ("Meta / Facebook", {"fields": ("facebook_pixel_code",), "description": "Paste the complete Pixel snippet supplied by Meta Events Manager."}),
        ("TikTok", {"fields": ("tiktok_pixel_code",), "description": "Paste the complete Pixel snippet supplied by TikTok Events Manager."}),
    )
    readonly_fields = ("updated_at",)

    def has_module_permission(self, request): return request.user.is_superuser
    def has_view_permission(self, request, obj=None): return request.user.is_superuser
    def has_change_permission(self, request, obj=None): return request.user.is_superuser
    def has_add_permission(self, request): return request.user.is_superuser and not TrackingPixelSettings.objects.exists()
    def has_delete_permission(self, request, obj=None): return False
