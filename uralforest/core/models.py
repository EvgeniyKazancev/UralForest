from django.core.validators import RegexValidator
from django.db import models

phone_validator = RegexValidator(
    regex=r"^\+?[0-9\s\-()]{7,20}$",
    message="Введите корректный номер телефона.",
)


class SingletonModel(models.Model):
    """Модель-одиночка: в базе всегда одна запись (pk=1)."""

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    @classmethod
    def load(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj


class SiteSettings(SingletonModel):
    """Глобальные настройки сайта. Редактируются в админке."""

    company_name = models.CharField("Название компании", max_length=200, default='ООО ТПК «Уральский лес»')
    short_name = models.CharField("Короткое название (для логотипа)", max_length=100, default="Уральский лес")
    logo = models.ImageField(
        "Логотип", upload_to="site/", blank=True, null=True,
        help_text="Небольшой логотип для шапки. PNG/SVG, высота ~40–48 px.",
    )
    tagline = models.CharField("Слоган", max_length=200, default="Пиломатериалы от производителя в Екатеринбурге")

    phone1 = models.CharField("Телефон 1", max_length=30, default="+7 (343) 200-77-74")
    phone2 = models.CharField("Телефон 2", max_length=30, blank=True, default="+7 (950) 202-19-33")
    phone3 = models.CharField("Телефон 3", max_length=30, blank=True)
    email = models.EmailField("E-mail", default="Ural_forest@bk.ru")

    whatsapp = models.CharField("WhatsApp (номер или ссылка)", max_length=200, blank=True, default="+79502021933")
    telegram = models.CharField("Telegram (ссылка или @ник)", max_length=200, blank=True)
    vk = models.CharField("ВКонтакте", max_length=200, blank=True)
    ok = models.CharField("Одноклассники", max_length=200, blank=True)

    address = models.CharField("Адрес склада/офиса", max_length=300, blank=True, default="г. Екатеринбург")
    work_hours = models.CharField("Режим работы", max_length=200, blank=True, default="Ежедневно с 9:00 до 20:00")
    map_embed = models.TextField(
        "Код карты (iframe)", blank=True,
        help_text="Вставьте HTML-код карты (Яндекс/Google) для отображения в разделе контактов.",
    )

    inn = models.CharField("ИНН", max_length=20, blank=True)
    ogrn = models.CharField("ОГРН", max_length=20, blank=True)
    kpp = models.CharField("КПП", max_length=20, blank=True)
    legal_address = models.CharField("Юридический адрес", max_length=300, blank=True)

    meta_title = models.CharField("SEO: Title", max_length=200, blank=True)
    meta_description = models.CharField("SEO: Description", max_length=300, blank=True)
    meta_keywords = models.CharField("SEO: Keywords", max_length=300, blank=True)

    hero_title = models.CharField("Заголовок первого экрана", max_length=200, blank=True, default="Пиломатериалы от производителя в Екатеринбурге")
    hero_subtitle = models.CharField("Подзаголовок первого экрана", max_length=300, blank=True, default="Доска, брус, вагонка — в наличии и под размер. Доставка по Екатеринбургу и Свердловской области.")
    hero_image = models.ImageField("Фоновое изображение первого экрана", upload_to="site/", blank=True, null=True)

    class Meta:
        verbose_name = "Настройки сайта"
        verbose_name_plural = "Настройки сайта"

    def __str__(self):
        return self.company_name

    @property
    def phones(self):
        return [p for p in [self.phone1, self.phone2, self.phone3] if p]

    @property
    def whatsapp_link(self):
        if not self.whatsapp:
            return ""
        if self.whatsapp.startswith("http"):
            return self.whatsapp
        digits = "".join(ch for ch in self.whatsapp if ch.isdigit())
        return f"https://wa.me/{digits}"


class Advantage(models.Model):
    """Преимущества («Почему мы»)."""

    title = models.CharField("Заголовок", max_length=150)
    text = models.TextField("Описание", blank=True)
    icon = models.CharField(
        "Иконка", max_length=50, blank=True,
        help_text="Имя иконки (например: gost, truck, team, wholesale, saw, calc).",
    )
    order = models.PositiveIntegerField("Порядок", default=0)
    is_active = models.BooleanField("Показывать", default=True)

    class Meta:
        ordering = ["order", "id"]
        verbose_name = "Преимущество"
        verbose_name_plural = "Преимущества"

    def __str__(self):
        return self.title


class WorkStep(models.Model):
    """Этапы работы («Как мы работаем»)."""

    title = models.CharField("Заголовок", max_length=150)
    text = models.CharField("Описание", max_length=250, blank=True)
    order = models.PositiveIntegerField("Порядок", default=0)
    is_active = models.BooleanField("Показывать", default=True)

    class Meta:
        ordering = ["order", "id"]
        verbose_name = "Этап работы"
        verbose_name_plural = "Этапы работы"

    def __str__(self):
        return self.title


class Service(models.Model):
    """Дополнительные услуги (доставка, распил, опт, подбор)."""

    title = models.CharField("Заголовок", max_length=150)
    text = models.TextField("Описание", blank=True)
    image = models.ImageField("Изображение", upload_to="services/", blank=True, null=True)
    order = models.PositiveIntegerField("Порядок", default=0)
    is_active = models.BooleanField("Показывать", default=True)

    class Meta:
        ordering = ["order", "id"]
        verbose_name = "Услуга"
        verbose_name_plural = "Услуги"

    def __str__(self):
        return self.title


class Application(models.Model):
    """Области применения («Где применяют»)."""

    title = models.CharField("Заголовок", max_length=150)
    text = models.TextField("Описание", blank=True)
    image = models.ImageField("Изображение", upload_to="applications/", blank=True, null=True)
    tags = models.CharField(
        "Связанные материалы", max_length=300, blank=True,
        help_text="Через запятую, например: Обрезной брус, Обрезная доска",
    )
    order = models.PositiveIntegerField("Порядок", default=0)
    is_active = models.BooleanField("Показывать", default=True)

    class Meta:
        ordering = ["order", "id"]
        verbose_name = "Область применения"
        verbose_name_plural = "Области применения"

    def __str__(self):
        return self.title

    @property
    def tag_list(self):
        return [t.strip() for t in self.tags.split(",") if t.strip()]


class Review(models.Model):
    """Отзывы."""

    name = models.CharField("Имя", max_length=100)
    role = models.CharField("Род деятельности", max_length=150, blank=True)
    location = models.CharField("Город / район", max_length=150, blank=True)
    text = models.TextField("Текст отзыва")
    products = models.CharField("Товары", max_length=200, blank=True)
    rating = models.PositiveSmallIntegerField("Оценка (1–5)", default=5)
    published_at = models.DateField("Дата", null=True, blank=True)
    is_published = models.BooleanField("Опубликован", default=True)
    order = models.PositiveIntegerField("Порядок", default=0)

    class Meta:
        ordering = ["order", "-published_at", "id"]
        verbose_name = "Отзыв"
        verbose_name_plural = "Отзывы"

    def __str__(self):
        return f"{self.name} — {self.role}".strip(" —")


class FAQ(models.Model):
    """Часто задаваемые вопросы."""

    question = models.CharField("Вопрос", max_length=300)
    answer = models.TextField("Ответ")
    order = models.PositiveIntegerField("Порядок", default=0)
    is_active = models.BooleanField("Показывать", default=True)

    class Meta:
        ordering = ["order", "id"]
        verbose_name = "Вопрос"
        verbose_name_plural = "Вопросы (FAQ)"

    def __str__(self):
        return self.question


class LeadRequest(models.Model):
    """Заявки: расчёт заказа, обратный звонок, вопрос."""

    class Kind(models.TextChoices):
        CALC = "calc", "Расчёт заказа"
        CALLBACK = "callback", "Обратный звонок"
        QUESTION = "question", "Вопрос"
        CONTACT = "contact", "Сообщение с контактов"

    class ContactMethod(models.TextChoices):
        PHONE = "phone", "Звонок"
        WHATSAPP = "whatsapp", "WhatsApp"
        TELEGRAM = "telegram", "Telegram"

    kind = models.CharField("Тип заявки", max_length=20, choices=Kind.choices, default=Kind.CALC)
    name = models.CharField("Имя", max_length=120)
    phone = models.CharField("Телефон", max_length=30, validators=[phone_validator])
    email = models.EmailField("E-mail", blank=True)
    material = models.CharField("Материал / объём", max_length=300, blank=True)
    message = models.TextField("Сообщение", blank=True)
    contact_method = models.CharField(
        "Способ связи", max_length=20, choices=ContactMethod.choices, default=ContactMethod.PHONE
    )
    consent = models.BooleanField("Согласие на обработку данных", default=True)
    is_processed = models.BooleanField("Обработана", default=False)
    created_at = models.DateTimeField("Создана", auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Заявка"
        verbose_name_plural = "Заявки"

    def __str__(self):
        return f"{self.get_kind_display()}: {self.name} ({self.phone})"
