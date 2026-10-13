from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from catalog.models import Product

from .cart import Cart


def _is_ajax(request):
    return request.headers.get("x-requested-with") == "XMLHttpRequest"


def cart_detail(request):
    cart = Cart(request)
    return render(request, "cart/detail.html", {"cart": cart})


@require_POST
def cart_add(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id, is_active=True)
    quantity = request.POST.get("quantity", "1")
    update = request.POST.get("update") == "1"
    cart.add(product, quantity=quantity, update=update)
    if _is_ajax(request):
        return JsonResponse({
            "ok": True,
            "count": len(cart),
            "total": f"{cart.total:.2f}",
            "message": f"«{product.name}» добавлен в корзину",
        })
    return redirect("cart:detail")


@require_POST
def cart_update(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    quantity = request.POST.get("quantity", "1")
    cart.add(product, quantity=quantity, update=True)
    return redirect("cart:detail")


@require_POST
def cart_remove(request, product_id):
    cart = Cart(request)
    cart.remove(product_id)
    if _is_ajax(request):
        return JsonResponse({"ok": True, "count": len(cart), "total": f"{cart.total:.2f}"})
    return redirect("cart:detail")
