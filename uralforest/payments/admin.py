from django.contrib import admin

from .models import Payment


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ("id", "order", "provider", "method", "amount", "status", "is_test", "created_at")
    list_filter = ("provider", "method", "status", "is_test", "created_at")
    search_fields = ("order__number", "external_id")
    readonly_fields = ("order", "provider", "method", "amount", "status", "external_id",
                       "confirmation_url", "is_test", "raw_response", "created_at", "paid_at")

    def has_add_permission(self, request):
        return False
