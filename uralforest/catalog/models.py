from django.db import models
from django.urls import reverse

from core.utils import make_slug


class Category(models.Model):
    """Категория каталога (например: Пиломатериал естественной влажности)."""

    name = models.CharField("Название", max_length=150)
    slug = models.SlugField("URL (slug)", max_length=160, unique=True, blank=True)
    short_description = models.CharField("Краткое описание", max_length=300, blank=True)
    description = models.TextField("Описание", blank=True)
    image = models.ImageField("Изображение", upload_to="categories/", blank=True, null=True)
    order = models.PositiveIntegerField("Порядок", default=0)
    is_active = models.BooleanField("Показывать", default=True)

    meta_title = models.CharField("SEO: Title", max_length=200, blank=True)
    meta_description = models.CharField("SEO: Description", max_length=300, blank=True)

    class Meta:
        ordering = ["order", "id"]
        verbose_name = "Категория"
        verbose_name_plural = "Категории"

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = make_slug(self.name)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("catalog:category", args=[self.slug])


class Product(models.Model):
    """Товар каталога: конкретное изделие/сечение."""

    class Unit(models.TextChoices):
        M3 = "m3", "м³"
        M2 = "m2", "м²"
        PCS = "pcs", "шт"
        PM = "pm", "пог. м"

    class Stock(models.TextChoices):
        IN_STOCK = "in_stock", "В наличии"
        TO_ORDER = "to_order", "Под заказ"
        OUT = "out", "Нет в наличии"

    category = models.ForeignKey(
        Category, on_delete=models.PROTECT, related_name="products", verbose_name="Категория"
    )
    name = models.CharField("Название", max_length=200)
    slug = models.SlugField("URL (slug)", max_length=220, unique=True, blank=True)
    short_description = models.CharField("Краткая карточка", max_length=300, blank=True)
    description = models.TextField("Описание", blank=True)

    unit = models.CharField("Единица измерения", max_length=5, choices=Unit.choices, default=Unit.M3)
    price = models.DecimalField("Цена за единицу, ₽", max_digits=12, decimal_places=2, default=0)
    old_price = models.DecimalField(
        "Старая цена, ₽", max_digits=12, decimal_places=2, blank=True, null=True
    )

    size = models.CharField("Размер, мм", max_length=100, blank=True, help_text="Например: 25×150×6000")
    thickness = models.CharField("Толщина, мм", max_length=50, blank=True)
    width = models.CharField("Ширина, мм", max_length=50, blank=True)
    length = models.CharField("Длина, мм", max_length=50, blank=True)
    wood_type = models.CharField("Порода", max_length=100, blank=True, help_text="Сосна, ель, лиственница…")
    grade = models.CharField("Сорт", max_length=50, blank=True, help_text="АВ, В, 1, 2…")
    moisture = models.CharField("Влажность", max_length=100, blank=True, help_text="Естественная, 8–16%…")
    per_cube = models.CharField("Штук в 1 м³", max_length=50, blank=True)

    image = models.ImageField("Главное изображение", upload_to="products/", blank=True, null=True)
    is_featured = models.BooleanField("На главной", default=False)
    is_active = models.BooleanField("Показывать", default=True)
    stock = models.CharField("Наличие", max_length=20, choices=Stock.choices, default=Stock.IN_STOCK)
    order = models.PositiveIntegerField("Порядок", default=0)
    created_at = models.DateTimeField("Добавлен", auto_now_add=True)
    updated_at = models.DateTimeField("Обновлён", auto_now=True)

    meta_title = models.CharField("SEO: Title", max_length=200, blank=True)
    meta_description = models.CharField("SEO: Description", max_length=300, blank=True)

    class Meta:
        ordering = ["order", "id"]
        verbose_name = "Товар"
        verbose_name_plural = "Товары"

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            base = self.name
            if self.size and self.size not in self.name:
                base = f"{self.name} {self.size}"
            self.slug = make_slug(base)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("catalog:product", args=[self.slug])

    @property
    def is_on_sale(self):
        return bool(self.old_price and self.old_price > self.price)

    @property
    def price_display(self):
        return f"{self.price:.0f} ₽/{self.get_unit_display()}"


class ProductImage(models.Model):
    """Дополнительные изображения товара."""

    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="images", verbose_name="Товар"
    )
    image = models.ImageField("Изображение", upload_to="products/gallery/")
    alt = models.CharField("Alt-текст", max_length=200, blank=True)
    order = models.PositiveIntegerField("Порядок", default=0)

    class Meta:
        ordering = ["order", "id"]
        verbose_name = "Изображение товара"
        verbose_name_plural = "Изображения товара"

    def __str__(self):
        return self.alt or f"Изображение #{self.pk}"
