import json

from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from orders.models import Order

from .gateways import get_gateway, yookassa_configured
from .models import Payment


def _map_method(order: Order) -> str:
    if order.payment_method == Order.PaymentMethod.SBP:
        return Payment.Method.SBP
    return Payment.Method.CARD


def start(request, order_number):
    order = get_object_or_404(Order, number=order_number)
    if order.payment_method not in (Order.PaymentMethod.CARD, Order.PaymentMethod.SBP):
        return redirect("orders:success", number=order.number)

    method = _map_method(order)
    gateway = get_gateway()
    return_url = request.build_absolute_uri(reverse("payments:return", args=[order.number]))
    description = f"Оплата заказа №{order.number} — {order.customer_name}"

    result = gateway.create_payment(order, method, return_url, description)

    if not result.success:
        messages.error(request, result.message or "Не удалось создать платёж. Попробуйте другой способ оплаты.")
        return redirect("orders:checkout")

    Payment.objects.create(
        order=order,
        provider=result.provider,
        method=method,
        amount=order.total,
        status=result.status if result.status in dict(Payment.Status.choices) else Payment.Status.PENDING,
        external_id=result.external_id,
        confirmation_url=result.confirmation_url,
        is_test=result.is_test,
        raw_response=result.raw,
    )
    order.payment_status = Order.PaymentStatus.PENDING
    order.save(update_fields=["payment_status"])

    if result.is_test:
        messages.info(request, result.message)
    return redirect(result.confirmation_url)


def mock_confirm(request, order_number):
    """Демонстрационная страница оплаты (пока ключи ЮKassa не заданы)."""
    order = get_object_or_404(Order, number=order_number)
    method = request.GET.get("method", "card")
    return render(request, "payments/mock.html", {"order": order, "method": method})


@require_POST
def mock_pay(request, order_number):
    order = get_object_or_404(Order, number=order_number)
    payment = order.payments.first()
    if payment:
        payment.status = Payment.Status.SUCCEEDED
        payment.paid_at = timezone.now()
        payment.save(update_fields=["status", "paid_at"])
    order.payment_status = Order.PaymentStatus.PAID
    order.status = Order.Status.PAID
    order.save(update_fields=["payment_status", "status"])
    messages.success(request, "Демо-оплата прошла успешно.")
    return redirect("orders:success", number=order.number)


@require_POST
def mock_cancel(request, order_number):
    order = get_object_or_404(Order, number=order_number)
    payment = order.payments.first()
    if payment:
        payment.status = Payment.Status.CANCELED
        payment.save(update_fields=["status"])
    order.payment_status = Order.PaymentStatus.FAILED
    order.save(update_fields=["payment_status"])
    messages.warning(request, "Оплата отменена.")
    return redirect("orders:success", number=order.number)


def return_view(request, order_number):
    """Пользователь вернулся с оплаты. Проверяем статус платежа у провайдера."""
    order = get_object_or_404(Order, number=order_number)
    payment = order.payments.first()
    if payment and payment.provider == Payment.Provider.YOOKASSA and payment.external_id and yookassa_configured():
        gateway = get_gateway()
        data = gateway.get_payment(payment.external_id)
        if data:
            _apply_status(payment, data.get("status", ""))
    return redirect("orders:success", number=order.number)


@csrf_exempt
@require_POST
def webhook(request):
    """HTTP-уведомление от ЮKassa."""
    try:
        payload = json.loads(request.body.decode("utf-8"))
    except (ValueError, UnicodeDecodeError):
        return JsonResponse({"ok": False, "error": "invalid json"}, status=400)

    event = payload.get("event", "")
    obj = payload.get("object") or {}
    external_id = obj.get("id", "")

    payment = Payment.objects.filter(external_id=external_id).first()
    if not payment:
        order_number = (obj.get("metadata") or {}).get("order_number")
        order = Order.objects.filter(number=order_number).first()
        payment = order.payments.first() if order else None

    if payment:
        status_map = {
            "payment.succeeded": Payment.Status.SUCCEEDED,
            "payment.waiting_for_capture": Payment.Status.WAITING,
            "payment.canceled": Payment.Status.CANCELED,
        }
        new_status = status_map.get(event) or obj.get("status")
        _apply_status(payment, new_status)
        payment.raw_response = payload
        payment.save(update_fields=["raw_response"])

    return JsonResponse({"ok": True})


def _apply_status(payment: Payment, status: str):
    payment.status = status
    if status == Payment.Status.SUCCEEDED:
        payment.paid_at = timezone.now()
        payment.order.payment_status = Order.PaymentStatus.PAID
        payment.order.status = Order.Status.PAID
        payment.order.save(update_fields=["payment_status", "status"])
    elif status in (Payment.Status.CANCELED, Payment.Status.FAILED):
        payment.order.payment_status = Order.PaymentStatus.FAILED
        payment.order.save(update_fields=["payment_status"])
    payment.save(update_fields=["status", "paid_at"])
