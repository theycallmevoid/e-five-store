import json

from django.shortcuts import get_object_or_404, redirect, render
from product.models import Product
from order.models import Order
from order.forms import CheckoutForm
from order.services.zrexpress import ZRExpressError, checkout_data, resolve_selection, sync_order
from store.models import StoreSettings, ZRExpressSettings


def home(request):
    products = Product.objects.filter(is_active=True)
    return render(request, "shop/home.html", {"products": products, "featured": products.filter(featured=True).first() or products.first(), "store": StoreSettings.current()})


def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug, is_active=True)
    form = CheckoutForm(request.POST if request.method == "POST" else None)
    try:
        delivery_data = checkout_data()
        delivery_error = ""
    except ZRExpressError as exc:
        delivery_data = {"wilayas": [], "communes": [], "rates": {}, "hubs": []}
        delivery_error = str(exc)
    if request.method == "POST" and form.is_valid():
        data = form.cleaned_data
        try:
            wilaya, commune, delivery_price, hub = resolve_selection(data["wilaya_id"], data["commune_id"], data["delivery_type"], data.get("hub_id"))
            order = Order.objects.create(product=product, full_name=data["full_name"], phone=data["phone"], wilaya_id=wilaya["id"], wilaya=wilaya["name"], commune_id=commune["id"], commune=commune["name"], pickup_hub_id=hub.get("id") if hub else None, pickup_hub_name=hub.get("name") if hub else "", address=data["address"], delivery_type=data["delivery_type"], product_price=product.price, delivery_price=delivery_price, total_price=product.price + delivery_price)
            if ZRExpressSettings.current().live_sync:
                sync_order(order)
            request.session["order_reference"] = order.reference
            return redirect("thank_you", reference=order.reference)
        except ZRExpressError as exc:
            form.add_error(None, str(exc))
    public_data = {
        "wilayas": [{"id": x.get("id"), "code": x.get("code"), "name": x.get("name")} for x in delivery_data["wilayas"]],
        "communes": [{"id": x.get("id"), "name": x.get("name"), "parentId": x.get("parentId")} for x in delivery_data["communes"]],
        "rates": delivery_data["rates"],
        "hubs": [{"id": x.get("id"), "name": x.get("name"), "address": {"street": (x.get("address") or {}).get("street"), "cityTerritoryId": (x.get("address") or {}).get("cityTerritoryId"), "districtTerritoryId": (x.get("address") or {}).get("districtTerritoryId")}} for x in delivery_data["hubs"]],
    }
    return render(request, "shop/product.html", {"product": product, "form": form, "delivery_error": delivery_error, "delivery_data_json": json.dumps(public_data, ensure_ascii=False), "store": StoreSettings.current()})


def thank_you(request, reference):
    order = get_object_or_404(Order, reference=reference)
    return render(request, "shop/thank_you.html", {"order": order, "product": order.product, "store": StoreSettings.current()})
