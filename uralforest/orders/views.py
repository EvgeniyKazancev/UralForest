from decimal import Decimal

from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render

from cart.cart import Cart

from .forms import CheckoutForm
from .models import Order, OrderItem


def checkout(request):
    cart = Cart(request)
    if cart.is_empty:
        messages.info(request, "Ваша корзина пуста. Добавьте товары из каталога.")
        return redirect("catalog:list")

    if request.method == "POST":
        form = CheckoutForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            order.total = cart.total
            order.save()
            for item in cart:
                OrderItem.objects.create(
                    order=order,
                    product=item["product"],
                    name=item["product"].name,
                    unit=item["product"].get_unit_display(),
                    price=item["price"],
                    quantity=item["quantity"],
                )
            order.recalc_total()
            cart.clear()

            if order.payment_method in (Order.PaymentMethod.CARD, Order.PaymentMethod.SBP):
                return redirect("payments:start", order_number=order.number)
            return redirect("orders:success", number=order.number)
    else:
        form = CheckoutForm()

    return render(request, "orders/checkout.html", {"form": form, "cart": cart})


def success(request, number):
    order = get_object_or_404(Order, number=number)
    return render(request, "orders/success.html", {"order": order})
