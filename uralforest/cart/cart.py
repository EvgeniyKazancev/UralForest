from decimal import Decimal, InvalidOperation

from django.conf import settings

from catalog.models import Product

CART_SESSION_ID = "cart"


def to_decimal(value, default="0"):
    try:
        return Decimal(str(value))
    except (InvalidOperation, TypeError, ValueError):
        return Decimal(default)


class Cart:
    """Корзина в сессии. Поддерживает дробные количества (м³, м², пог. м)."""

    def __init__(self, request):
        self.session = request.session
        cart = self.session.get(CART_SESSION_ID)
        if not cart:
            cart = self.session[CART_SESSION_ID] = {}
        self.cart = cart

    def add(self, product: Product, quantity=1, update=False):
        key = str(product.id)
        quantity = to_decimal(quantity, "1")
        if quantity <= 0:
            quantity = Decimal("1")
        if key not in self.cart:
            self.cart[key] = {
                "quantity": str(quantity),
                "price": str(product.price),
                "unit": product.unit,
            }
        elif update:
            self.cart[key]["quantity"] = str(quantity)
        else:
            self.cart[key]["quantity"] = str(to_decimal(self.cart[key]["quantity"]) + quantity)
        self.cart[key]["price"] = str(product.price)
        self.save()

    def remove(self, product_id):
        key = str(product_id)
        if key in self.cart:
            del self.cart[key]
            self.save()

    def clear(self):
        self.session[CART_SESSION_ID] = {}
        self.session.modified = True
        self.cart = {}

    def save(self):
        self.session.modified = True

    def __iter__(self):
        product_ids = self.cart.keys()
        products = Product.objects.filter(id__in=product_ids)
        products_map = {str(p.id): p for p in products}
        for key, item in self.cart.items():
            product = products_map.get(key)
            if not product:
                continue
            quantity = to_decimal(item["quantity"])
            price = to_decimal(item["price"])
            yield {
                "product": product,
                "quantity": quantity,
                "price": price,
                "total": (price * quantity).quantize(Decimal("0.01")),
            }

    def __len__(self):
        return len(self.cart)

    @property
    def total(self):
        return sum((item["total"] for item in self), Decimal("0.00")).quantize(Decimal("0.01"))

    @property
    def is_empty(self):
        return len(self.cart) == 0
