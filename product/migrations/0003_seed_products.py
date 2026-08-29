from django.db import migrations


PRODUCTS = [
    {
        "slug": "ultra-waves-sea-salt-spray", "sku": "EFIVE-ULTRAWAVES-200", "price": 2500,
        "badge": "BEST-SELLER", "name_en": "The Ultra Waves", "subtitle_en": "Sea Salt Spray · 200 ml",
        "description_en": "A lightweight sea salt spray for natural waves, texture and volume.",
        "benefits_en": "Instant volume and texture\nNatural matte finish\nFor all hair types",
        "usage_en": "Shake well, spray onto damp or dry hair, then style with your hands.",
        "main_image": "products/product-main.jpg", "featured": True, "sort_order": 1,
        "zr_product_id": "2d99d323-f524-42ac-b120-3b73b8f3a486", "length": 20, "width": 6, "height": 6, "weight": "0.25",
        "gallery": ["products/gallery/WhatsApp_Image_2026-08-19_at_07.30.51_2.jpeg"],
    },
    {
        "slug": "styling-cream", "sku": "EFIVE-STYLING-CREAM-50", "price": 1500,
        "badge": "NEW", "name_en": "E Five Styling Cream", "subtitle_en": "Keratin Cream · 50 g",
        "description_en": "A keratin styling cream with natural shine and flexible hold.",
        "benefits_en": "Flexible long-lasting hold\nNatural shine\nEasy to carry",
        "usage_en": "Warm a small amount between your palms then apply to hair.",
        "main_image": "products/cream-main.png", "sort_order": 2,
        "zr_product_id": "871564aa-bd79-473b-a494-10e064d55b33", "length": 8, "width": 8, "height": 5, "weight": "0.08",
        "gallery": ["products/gallery/cream-angle.png", "products/gallery/cream-close.png", "products/gallery/cream-lifestyle.jpg"],
    },
    {
        "slug": "pack-sea-salt-styling-cream", "sku": "EFIVE-PACK-WAVES-CREAM", "price": 4000,
        "badge": "COMPLETE PACK", "name_en": "E Five Pack", "subtitle_en": "Sea Salt Spray + Styling Cream",
        "description_en": "The complete duo for texture, volume and flexible hold.",
        "benefits_en": "Two complementary products\nVolume, texture and hold\nComplete routine",
        "usage_en": "Use the spray first, then finish with a small amount of cream.",
        "main_image": "products/pack-main.png", "sort_order": 3,
        "zr_product_id": "e2d7c02d-64a0-46fe-83f3-5272b6f40782", "length": 22, "width": 12, "height": 8, "weight": "0.35",
        "gallery": ["products/gallery/pack-alt-1.png", "products/gallery/pack-alt-2.png", "products/gallery/pack-alt-3.png", "products/gallery/pack-cream.png", "products/gallery/pack-lifestyle.jpg"],
    },
]


def seed_products(apps, schema_editor):
    Product = apps.get_model("product", "Product")
    ProductImage = apps.get_model("product", "ProductImage")
    for row in PRODUCTS:
        gallery = row.pop("gallery")
        product, _ = Product.objects.get_or_create(slug=row["slug"], defaults=row)
        for index, image in enumerate(gallery, 1):
            ProductImage.objects.get_or_create(product=product, image=image, defaults={"alt_text": row["name_en"], "sort_order": index})


class Migration(migrations.Migration):
    dependencies = [("product", "0002_product_height_product_length_product_weight_and_more")]
    operations = [migrations.RunPython(seed_products, migrations.RunPython.noop)]
