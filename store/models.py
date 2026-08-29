from django.db import models


class StoreSettings(models.Model):
    brand_name = models.CharField(max_length=80, default="E Five")
    logo = models.ImageField(upload_to="branding/", blank=True)
    announcement_en = models.CharField(max_length=160, default="Delivery across Algeria")
    announcement_fr = models.CharField(max_length=160, blank=True)
    announcement_ar = models.CharField(max_length=160, blank=True)
    hero_title_en = models.CharField(max_length=160, default="Your hair. Your wave.")
    hero_title_fr = models.CharField(max_length=160, blank=True)
    hero_title_ar = models.CharField(max_length=160, blank=True)
    hero_text_en = models.TextField(default="Texture, volume and natural movement. Discover effortless styling made for you.")
    hero_text_fr = models.TextField(blank=True)
    hero_text_ar = models.TextField(blank=True)
    hero_image = models.ImageField(upload_to="branding/", blank=True)
    def save(self, *args, **kwargs): self.pk = 1; return super().save(*args, **kwargs)
    @classmethod
    def current(cls): return cls.objects.get_or_create(pk=1)[0]
    def __str__(self): return "Store settings"


class ZRExpressSettings(models.Model):
    api_base = models.URLField(default="https://api.zrexpress.app/api/v1")
    tenant_id = models.UUIDField(blank=True, null=True)
    secret_key = models.CharField(max_length=255, blank=True)
    live_sync = models.BooleanField(default=False, help_text="Create a ZR Express parcel immediately after checkout")

    def save(self, *args, **kwargs):
        self.pk = 1
        return super().save(*args, **kwargs)

    @classmethod
    def current(cls):
        return cls.objects.get_or_create(pk=1)[0]

    @property
    def configured(self):
        return bool(self.tenant_id and self.secret_key)

    def __str__(self):
        return "ZR Express settings"


class TrackingPixelSettings(models.Model):
    enabled = models.BooleanField(default=False, help_text="Enable the saved tracking snippets across all storefront pages")
    facebook_pixel_code = models.TextField(blank=True, help_text="Paste the complete Meta/Facebook Pixel JavaScript snippet")
    tiktok_pixel_code = models.TextField(blank=True, help_text="Paste the complete TikTok Pixel JavaScript snippet")
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        self.pk = 1
        return super().save(*args, **kwargs)

    @classmethod
    def current(cls):
        return cls.objects.get_or_create(pk=1)[0]

    def __str__(self):
        return "Facebook and TikTok pixels"
