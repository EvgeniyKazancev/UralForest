from django.contrib import admin
from django.utils.html import format_html

from .models import Category, Product, ProductImage


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "order", "is_active", "products_count")
    list_editable = ("order", "is_active")
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ("name", "short_description")

    @admin.display(description="Товаров")
    def products_count(self, obj):
        return obj.products.count()


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        "name", "category", "size", "unit", "price", "stock", "is_featured", "is_active", "preview",
    )
    list_editable = ("price", "stock", "is_featured", "is_active")
    list_filter = ("category", "unit", "stock", "is_featured", "is_active", "wood_type")
    search_fields = ("name", "size", "wood_type", "grade")
    prepopulated_fields = {"slug": ("name",)}
    inlines = [ProductImageInline]
    list_select_related = ("category",)
    save_on_top = True
    fieldsets = (
        ("Основное", {"fields": ("category", "name", "slug", "short_description", "description", "image")}),
        ("Цена и единицы", {"fields": ("unit", "price", "old_price")}),
        ("Характеристики", {"fields": ("size", "thickness", "width", "length", "wood_type", "grade", "moisture", "per_cube")}),
        ("Показ", {"fields": ("stock", "is_featured", "is_active", "order")}),
        ("SEO", {"fields": ("meta_title", "meta_description")}),
    )

    @admin.display(description="Фото")
    def preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="height:40px;border-radius:4px;" />', obj.image.url)
        return "—"
