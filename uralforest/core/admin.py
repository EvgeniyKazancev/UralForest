from django.contrib import admin

from .models import (
    Advantage,
    Application,
    FAQ,
    LeadRequest,
    Review,
    Service,
    SiteSettings,
    WorkStep,
)


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    list_display = ("company_name", "phone1", "email", "work_hours")
    fieldsets = (
        ("Бренд", {"fields": ("company_name", "short_name", "logo", "tagline")}),
        ("Контакты", {"fields": ("phone1", "phone2", "phone3", "email", "work_hours")}),
        ("Мессенджеры и соцсети", {"fields": ("whatsapp", "telegram", "vk", "ok")}),
        ("Адрес и карта", {"fields": ("address", "legal_address", "map_embed")}),
        ("Реквизиты", {"fields": ("inn", "ogrn", "kpp")}),
        ("Первый экран", {"fields": ("hero_title", "hero_subtitle", "hero_image")}),
        ("SEO", {"fields": ("meta_title", "meta_description", "meta_keywords")}),
    )

    def has_add_permission(self, request):
        return not SiteSettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(Advantage)
class AdvantageAdmin(admin.ModelAdmin):
    list_display = ("title", "icon", "order", "is_active")
    list_editable = ("order", "is_active")
    list_filter = ("is_active",)
    search_fields = ("title", "text")


@admin.register(WorkStep)
class WorkStepAdmin(admin.ModelAdmin):
    list_display = ("title", "order", "is_active")
    list_editable = ("order", "is_active")


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ("title", "order", "is_active")
    list_editable = ("order", "is_active")
    search_fields = ("title", "text")


@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ("title", "order", "is_active")
    list_editable = ("order", "is_active")
    search_fields = ("title", "tags")


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ("name", "role", "rating", "is_published", "published_at", "order")
    list_editable = ("is_published", "order")
    list_filter = ("is_published", "rating")
    search_fields = ("name", "text", "products")


@admin.register(FAQ)
class FAQAdmin(admin.ModelAdmin):
    list_display = ("question", "order", "is_active")
    list_editable = ("order", "is_active")
    search_fields = ("question", "answer")


@admin.register(LeadRequest)
class LeadRequestAdmin(admin.ModelAdmin):
    list_display = ("created_at", "kind", "name", "phone", "contact_method", "is_processed")
    list_filter = ("kind", "contact_method", "is_processed", "created_at")
    list_editable = ("is_processed",)
    search_fields = ("name", "phone", "email", "message")
    readonly_fields = ("kind", "name", "phone", "email", "material", "message", "contact_method", "consent", "created_at")

    def has_add_permission(self, request):
        return False
