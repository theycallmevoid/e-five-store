import json
import uuid
from decimal import Decimal
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from django.core.cache import cache

from store.models import ZRExpressSettings


class ZRExpressError(Exception):
    pass


def configuration():
    config = ZRExpressSettings.current()
    if not config.configured:
        raise ZRExpressError("ZR Express is not configured. Add its credentials in Django Admin.")
    return config


def _json_default(value):
    if isinstance(value, Decimal):
        return float(value)
    if isinstance(value, uuid.UUID):
        return str(value)
    raise TypeError(f"Object of type {type(value).__name__} is not JSON serializable")


def request_api(path, method="GET", payload=None):
    config = configuration()
    data = json.dumps(payload, default=_json_default).encode("utf-8") if payload is not None else None
    request = Request(
        f"{config.api_base.rstrip('/')}{path}", data=data, method=method,
        headers={"Accept": "application/json", "Content-Type": "application/json", "X-Tenant": str(config.tenant_id), "X-Api-Key": config.secret_key},
    )
    try:
        with urlopen(request, timeout=20) as response:
            body = response.read().decode("utf-8")
            return json.loads(body) if body else {}
    except HTTPError as exc:
        detail = ""
        try:
            error = json.loads(exc.read().decode("utf-8"))
            detail = error.get("detail") or error.get("title") or ""
        except (ValueError, UnicodeDecodeError):
            pass
        raise ZRExpressError(detail or f"ZR Express returned error {exc.code}.") from exc
    except (URLError, TimeoutError) as exc:
        raise ZRExpressError("ZR Express is temporarily unavailable.") from exc


def get_territories():
    config = configuration()
    key = f"zr-territories-{config.tenant_id}"
    if (cached := cache.get(key)) is not None:
        return cached
    items, page = [], 1
    while True:
        response = request_api("/territories/search", "POST", {"pageNumber": page, "pageSize": 1000, "orderBy": ["code asc"], "includeUnavailable": False})
        items.extend(response.get("items") or [])
        if not response.get("hasNext"):
            break
        page += 1
    cache.set(key, items, 3600)
    return items


def get_rates():
    config = configuration()
    key = f"zr-rates-{config.tenant_id}"
    if (cached := cache.get(key)) is not None:
        return cached
    rates = request_api("/delivery-pricing/rates").get("rates") or []
    cache.set(key, rates, 900)
    return rates


def get_hubs():
    config = configuration()
    key = f"zr-hubs-{config.tenant_id}"
    if (cached := cache.get(key)) is not None:
        return cached
    response = request_api("/hubs/search", "POST", {"pageNumber": 1, "pageSize": 1000, "orderBy": ["name asc"], "includeServices": False})
    hubs = [item for item in response.get("items", []) if item.get("isPickupPoint")]
    cache.set(key, hubs, 3600)
    return hubs


def checkout_data():
    territories = get_territories()
    wilayas = sorted((x for x in territories if (x.get("level") or "").lower() == "wilaya"), key=lambda x: (x.get("code") or 999, x.get("name") or ""))
    communes = sorted((x for x in territories if (x.get("level") or "").lower() == "commune"), key=lambda x: x.get("name") or "")
    rates = {str(x.get("toTerritoryId")): x.get("deliveryPrices") or [] for x in get_rates()}
    return {"wilayas": wilayas, "communes": communes, "rates": rates, "hubs": get_hubs()}


def resolve_selection(wilaya_id, commune_id, delivery_type, hub_id=None):
    data = checkout_data()
    wilaya = next((x for x in data["wilayas"] if str(x.get("id")) == str(wilaya_id)), None)
    commune = next((x for x in data["communes"] if str(x.get("id")) == str(commune_id)), None)
    if not wilaya or not commune or str(commune.get("parentId")) != str(wilaya.get("id")):
        raise ZRExpressError("The selected wilaya or commune is invalid.")
    prices = data["rates"].get(str(commune["id"])) or data["rates"].get(str(wilaya["id"])) or []
    price = next((x.get("price") for x in prices if x.get("deliveryType") == delivery_type), None)
    if price is None:
        raise ZRExpressError("No ZR Express rate is available for this delivery choice.")
    hub = None
    if delivery_type == "pickup-point":
        hub = next((x for x in data["hubs"] if str(x.get("id")) == str(hub_id)), None)
        address = (hub or {}).get("address") or {}
        if not hub or (str(address.get("districtTerritoryId")) != str(commune["id"]) and str(address.get("cityTerritoryId")) != str(wilaya["id"])):
            raise ZRExpressError("The selected pickup point is invalid.")
    return wilaya, commune, int(round(float(price))), hub


def create_parcel(order):
    product = order.product
    ordered_product = {"productName": product.name_en, "productSku": product.sku, "unitPrice": order.product_price, "quantity": 1, "length": product.length, "width": product.width, "height": product.height, "weight": float(product.weight), "stockType": "local" if product.zr_product_id else "none"}
    if product.zr_product_id:
        ordered_product["productId"] = str(product.zr_product_id)
    payload = {"customer": {"customerId": str(uuid.uuid4()), "name": order.full_name, "phone": {"number1": order.phone}}, "deliveryAddress": {"cityTerritoryId": str(order.wilaya_id), "districtTerritoryId": str(order.commune_id), "street": order.address}, "orderedProducts": [ordered_product], "amount": order.total_price, "description": f"{product.name_en} — {order.reference}", "deliveryType": order.delivery_type, "externalId": order.reference, "weight": {"weight": float(product.weight)}}
    if order.delivery_type == "pickup-point" and order.pickup_hub_id:
        payload["hubId"] = str(order.pickup_hub_id)
    return request_api("/parcels", "POST", payload)


def sync_order(order):
    try:
        response = create_parcel(order)
        order.zr_parcel_id = response.get("id")
        order.zr_sync_status = "synced"
        order.zr_error = ""
    except ZRExpressError as exc:
        order.zr_sync_status = "failed"
        order.zr_error = str(exc)
    order.save(update_fields=["zr_parcel_id", "zr_sync_status", "zr_error"])
    return order.zr_sync_status == "synced"
