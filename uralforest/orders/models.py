from decimal import Decimal

from django.db import models
from django.utils import timezone


class Order(models.Model):
    class Status(models.TextChoices):
        NEW = "new", "Новый"
        CONFIRMED = "confirmed", "Подтверждён"
        PAID = "paid", "Оплачен"
        SHIPPED = "shipped", "Отгружен"
        DONE = "done", "Выполнен"
        CANCELED = "canceled", "Отменён"

    class Delivery(models.TextChoices):
        DELIVERY = "delivery", "Доставка"
        PICKUP = "pickup", "Самовывоз"

    class PaymentMethod(models.TextChoices):
        CARD = "card", "Оплата картой"
        SBP = "sbp", "СБП (по QR-коду)"
        INVOICE = "invoice", "Счёт для юрлица"
        CASH = "cash", "Наличные при получении"

    class PaymentStatus(models.TextChoices):
        NOT_PAID = "not_paid", "Не оплачен"
        PENDING = "pending", "Ожидает оплаты"
        PAID = "paid", "Оплачен"
        REFUNDED = "refunded", "Возврат"
        FAILED = "failed", "Ошибка оплаты"

    number = models.CharField("Номер заказа", max_length=20, unique=True, blank=True)
    status = models.CharField("Статус заказа", max_length=20, choices=Status.choices, default=Status.NEW)

    customer_name = models.CharField("Имя", max_length=150)
    phone = models.CharField("Телефон", max_length=30)
    email = models.EmailField("E-mail", blank=True)
    company = models.CharField("Компания", max_length=200, blank=True)
    comment = models.TextField("Комментарий", blank=True)

    delivery_method = models.CharField("Способ получения", max_length=20, choices=Delivery.choices, default=Delivery.DELIVERY)
    address = models.CharField("Адрес доставки", max_length=300, blank=True)

    payment_method = models.CharField("Способ оплаты", max_length=20, choices=PaymentMethod.choices, default=PaymentMethod.CARD)
    payment_status = models.CharField("Статус оплаты", max_length=20, choices=PaymentStatus.choices, default=PaymentStatus.NOT_PAID)

    total = models.DecimalField("Итого, ₽", max_digits=14, decimal_places=2, default=0)
    consent = models.BooleanField("Согласие на обработку данных", default=True)

    created_at = models.DateTimeField("Создан", default=timezone.now)
    updated_at = models.DateTimeField("Обновлён", auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Заказ"
        verbose_name_plural = "Заказы"

    def __str__(self):
        return f"Заказ №{self.number}"

    def save(self, *args, **kwargs):
        if not self.number:
            self.number = self._generate_number()
        super().save(*args, **kwargs)

    def _generate_number(self):
        last = Order.objects.order_by("-id").first()
        next_id = (last.id + 1) if last else 1
        return f"{timezone.now():%y%m%d}-{next_id:04d}"

    def recalc_total(self):
        self.total = sum((item.total for item in self.items.all()), Decimal("0.00"))
        self.save(update_fields=["total"])

    @property
    def is_paid(self):
        return self.payment_status == self.PaymentStatus.PAID


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items", verbose_name="Заказ")
    product = models.ForeignKey(
        "catalog.Product", on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Товар"
    )
    name = models.CharField("Наименование", max_length=250)
    unit = models.CharField("Единица", max_length=20, blank=True)
    price = models.DecimalField("Цена, ₽", max_digits=12, decimal_places=2)
    quantity = models.DecimalField("Количество", max_digits=12, decimal_places=3, default=1)
    total = models.DecimalField("Сумма, ₽", max_digits=14, decimal_places=2, default=0)

    class Meta:
        verbose_name = "Позиция заказа"
        verbose_name_plural = "Позиции заказа"

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.total = (self.price * self.quantity).quantize(self.price)
        super().save(*args, **kwargs)
