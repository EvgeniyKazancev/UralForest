"""Платёжные шлюзы.

Пока ключи ЮKassa не заданы в .env, используется демо-шлюз (MockGateway):
он проводит пользователя по тому же сценарию, что и реальный провайдер,
но не списывает деньги. После добавления ключей оплата включается автоматически.
"""

from __future__ import annotations

import base64
import json
import uuid
from dataclasses import dataclass, field
from decimal import Decimal
from urllib import error, request as urllib_request

from django.conf import settings
from django.urls import reverse

YOOKASSA_API_URL = "https://api.yookassa.ru/v3/payments"


@dataclass
class PaymentResult:
    success: bool
    provider: str
    method: str
    status: str
    external_id: str = ""
    confirmation_url: str = ""
    is_test: bool = True
    message: str = ""
    raw: dict = field(default_factory=dict)


class BaseGateway:
    provider = "base"
    is_test = True

    def create_payment(self, order, method: str, return_url: str, description: str) -> PaymentResult:
        raise NotImplementedError


class MockGateway(BaseGateway):
    """Демонстрационный шлюз. Реальной оплаты не производит."""

    provider = "mock"
    is_test = True

    def create_payment(self, order, method: str, return_url: str, description: str) -> PaymentResult:
        internal = reverse("payments:mock_confirm", args=[order.number]) + f"?method={method}"
        return PaymentResult(
            success=True,
            provider=self.provider,
            method=method,
            status="pending",
            external_id=f"mock-{uuid.uuid4().hex[:12]}",
            confirmation_url=internal,
            is_test=True,
            message="Демо-режим: реальная оплата не списывается. Подключите ключи ЮKassa в .env.",
            raw={"demo": True, "amount": str(order.total), "method": method},
        )


class YooKassaGateway(BaseGateway):
    """Реальный шлюз ЮKassa (карты и СБП)."""

    provider = "yookassa"
    is_test = False

    def __init__(self, shop_id: str, secret_key: str):
        self.shop_id = shop_id
        self.secret_key = secret_key

    def _auth_header(self) -> str:
        token = base64.b64encode(f"{self.shop_id}:{self.secret_key}".encode()).decode()
        return f"Basic {token}"

    def _payment_method_data(self, method: str) -> dict:
        if method == "sbp":
            return {"type": "sbp"}
        return {"type": "bank_card"}

    def create_payment(self, order, method: str, return_url: str, description: str) -> PaymentResult:
        payload = {
            "amount": {"value": f"{order.total:.2f}", "currency": "RUB"},
            "capture": True,
            "payment_method_data": self._payment_method_data(method),
            "confirmation": {"type": "redirect", "return_url": return_url},
            "description": description[:128],
            "metadata": {"order_number": order.number},
        }
        body = json.dumps(payload).encode("utf-8")
        req = urllib_request.Request(YOOKASSA_API_URL, data=body, method="POST")
        req.add_header("Authorization", self._auth_header())
        req.add_header("Content-Type", "application/json")
        req.add_header("Idempotence-Key", str(uuid.uuid4()))

        try:
            with urllib_request.urlopen(req, timeout=20) as resp:
                data = json.loads(resp.read().decode("utf-8"))
        except error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="ignore")
            return PaymentResult(
                success=False,
                provider=self.provider,
                method=method,
                status="failed",
                is_test=False,
                message=f"ЮKassa вернула ошибку {exc.code}: {detail[:300]}",
            )
        except Exception as exc:  # noqa: BLE001
            return PaymentResult(
                success=False,
                provider=self.provider,
                method=method,
                status="failed",
                is_test=False,
                message=f"Не удалось связаться с ЮKassa: {exc}",
            )

        confirmation = data.get("confirmation") or {}
        return PaymentResult(
            success=True,
            provider=self.provider,
            method=method,
            status=data.get("status", "pending"),
            external_id=data.get("id", ""),
            confirmation_url=confirmation.get("confirmation_url", ""),
            is_test=False,
            message="",
            raw=data,
        )

    def get_payment(self, external_id: str) -> dict | None:
        req = urllib_request.Request(f"{YOOKASSA_API_URL}/{external_id}", method="GET")
        req.add_header("Authorization", self._auth_header())
        try:
            with urllib_request.urlopen(req, timeout=20) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except Exception:  # noqa: BLE001
            return None


def yookassa_configured() -> bool:
    return bool(settings.YOOKASSA_SHOP_ID and settings.YOOKASSA_SECRET_KEY)


def get_gateway() -> BaseGateway:
    """Возвращает активный шлюз: ЮKassa, если заданы ключи, иначе демо."""
    if settings.PAYMENTS_ENABLED and yookassa_configured():
        return YooKassaGateway(settings.YOOKASSA_SHOP_ID, settings.YOOKASSA_SECRET_KEY)
    return MockGateway()


def amount_str(value) -> str:
    return f"{Decimal(value):.2f}"
