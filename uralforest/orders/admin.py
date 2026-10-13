from django.contrib import admin

from .models import Order, OrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ("total",)


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        "number", "created_at", "customer_name", "phone", "status",
        "payment_method", "payment_status", "total",
    )
    list_filter = ("status", "payment_status", "payment_method", "delivery_method", "created_at")
    search_fields = ("number", "customer_name", "phone", "email", "company")
    readonly_fields = ("number", "created_at", "updated_at", "total")
    inlines = [OrderItemInline]
    date_hierarchy = "created_at"
    fieldsets = (
        ("Заказ", {"fields": ("number", "status", "created_at", "updated_at")}),
        ("Клиент", {"fields": ("customer_name", "phone", "email", "company", "comment")}),
        ("Доставка", {"fields": ("delivery_method", "address")}),
        ("Оплата", {"fields": ("payment_method", "payment_status", "total")}),
    )
