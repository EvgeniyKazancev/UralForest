from django.db import models


class Payment(models.Model):
    class Provider(models.TextChoices):
        YOOKASSA = "yookassa", "ЮKassa"
        MOCK = "mock", "Демо-платёж"
        MANUAL = "manual", "Вручную"

    class Method(models.TextChoices):
        CARD = "card", "Банковская карта"
        SBP = "sbp", "СБП"

    class Status(models.TextChoices):
        PENDING = "pending", "Создан"
        WAITING = "waiting_for_capture", "Ожидает подтверждения"
        SUCCEEDED = "succeeded", "Оплачен"
        CANCELED = "canceled", "Отменён"
        FAILED = "failed", "Ошибка"

    order = models.ForeignKey(
        "orders.Order", on_delete=models.CASCADE, related_name="payments", verbose_name="Заказ"
    )
    provider = models.CharField("Провайдер", max_length=20, choices=Provider.choices, default=Provider.MOCK)
    method = models.CharField("Способ оплаты", max_length=10, choices=Method.choices, default=Method.CARD)
    amount = models.DecimalField("Сумма, ₽", max_digits=14, decimal_places=2)
    status = models.CharField("Статус", max_length=30, choices=Status.choices, default=Status.PENDING)

    external_id = models.CharField("ID платежа у провайдера", max_length=100, blank=True)
    confirmation_url = models.URLField("Ссылка на оплату", max_length=1000, blank=True)
    is_test = models.BooleanField("Тестовый режим", default=True)
    raw_response = models.JSONField("Ответ провайдера", blank=True, null=True)

    created_at = models.DateTimeField("Создан", auto_now_add=True)
    paid_at = models.DateTimeField("Оплачен", null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Платёж"
        verbose_name_plural = "Платежи"

    def __str__(self):
        return f"Платёж #{self.pk} по заказу {self.order.number} — {self.get_status_display()}"
