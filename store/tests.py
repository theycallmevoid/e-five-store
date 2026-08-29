from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from unittest.mock import patch
import uuid
import json
from decimal import Decimal

from order.models import Order
from product.models import Product, ProductImage
from order.services.zrexpress import _json_default
from store.models import TrackingPixelSettings


class StoreFlowTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.product = Product.objects.create(
            slug="test-product", sku="TEST-1", price=2500, name_en="Test Product",
            subtitle_en="Test subtitle", description_en="Test description",
            benefits_en="First benefit\nSecond benefit", usage_en="Use carefully.",
            main_image="products/test.jpg", is_active=True, featured=True,
        )
        ProductImage.objects.create(product=cls.product, image="products/gallery/test.jpg")

    def test_home_and_product_pages(self):
        self.assertEqual(self.client.get(reverse("home")).status_code, 200)
        response = self.client.get(reverse("product_detail", args=[self.product.slug]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "product-slider")
        self.assertContains(response, "Order now")

    def test_invalid_checkout_shows_errors_without_order(self):
        response = self.client.post(reverse("product_detail", args=[self.product.slug]), {})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "errorlist")
        self.assertEqual(Order.objects.count(), 0)

    def test_valid_checkout_reaches_thank_you(self):
        wilaya_id, commune_id = uuid.uuid4(), uuid.uuid4()
        with patch("store.views.resolve_selection", return_value=({"id": wilaya_id, "name": "Alger"}, {"id": commune_id, "name": "Alger Centre"}, 500, None)):
            response = self.client.post(reverse("product_detail", args=[self.product.slug]), {
                "full_name": "Test Customer", "phone": "0550000000",
                "wilaya_id": wilaya_id, "commune_id": commune_id,
                "address": "Test address 1", "delivery_type": "home",
            })
        order = Order.objects.get()
        self.assertEqual(order.delivery_price, 500)
        self.assertEqual(order.total_price, 3000)
        self.assertRedirects(response, reverse("thank_you", args=[order.reference]))
        self.assertContains(self.client.get(reverse("thank_you", args=[order.reference])), order.reference)

    def test_admin_catalog_is_available(self):
        admin = get_user_model().objects.create_superuser("qa-admin", "qa@example.com", "temporary-test-password")
        self.client.force_login(admin)
        self.assertEqual(self.client.get(reverse("admin:index")).status_code, 200)
        self.assertEqual(self.client.get(reverse("admin:product_product_changelist")).status_code, 200)
        self.assertEqual(self.client.get(reverse("admin:store_zrexpresssettings_changelist")).status_code, 200)

    def test_zr_payload_values_are_json_serializable(self):
        payload = {"weight": self.product.weight, "id": uuid.uuid4(), "price": Decimal("2500.00")}
        encoded = json.dumps(payload, default=_json_default)
        self.assertIn('"weight": 0.2', encoded)

    def test_tracking_pixels_are_admin_controlled(self):
        tracking = TrackingPixelSettings.current()
        tracking.facebook_pixel_code = "<script>window.facebookPixelLoaded=true;</script>"
        tracking.tiktok_pixel_code = "<script>window.tiktokPixelLoaded=true;</script>"
        tracking.enabled = False
        tracking.save()
        disabled = self.client.get(reverse("home"))
        self.assertNotContains(disabled, "facebookPixelLoaded")
        self.assertNotContains(disabled, "tiktokPixelLoaded")

        tracking.enabled = True
        tracking.save()
        enabled = self.client.get(reverse("home"))
        self.assertContains(enabled, "window.facebookPixelLoaded=true")
        self.assertContains(enabled, "window.tiktokPixelLoaded=true")
