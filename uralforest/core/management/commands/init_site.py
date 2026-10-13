"""Первичная настройка сайта.

Создаёт суперпользователя, категории каталога, контакты и стартовый контент.
Запуск:
    python manage.py init_site
    python manage.py init_site --username admin --password MyPass123 --with-demo
"""

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import transaction

from catalog.models import Category, Product
from core.models import (
    Advantage,
    Application,
    FAQ,
    Service,
    SiteSettings,
    WorkStep,
)

DEFAULT_CATEGORIES = [
    ("Пиломатериал естественной влажности", "Доска и брус естественной влажности 18–22% для черновых работ, опалубки и каркаса."),
    ("Пиломатериал камерной сушки", "Сухой пиломатериал 8–16% — держит геометрию, подходит для полов и конструкций."),
    ("Пиломатериал строганный, камерной сушки", "Строганые изделия камерной сушки с гладкой поверхностью для отделки."),
    ("Пиломатериал антисептированный", "Обработанные защитными составами материалы для влажных условий и наружных работ."),
    ("Деревянные дома, беседки", "Готовые деревянные конструкции: дома, беседки, хозблоки под заказ."),
]

DEFAULT_ADVANTAGES = [
    ("Материал по ГОСТ", "Сосна, ель, лиственница. Сорт и влажность — как в спецификации."),
    ("Доставка по Екатеринбургу и области", "Свой транспорт, выгрузка манипулятором прямо на объекте."),
    ("Подбор под объект", "Порода, сечение и сорт — по проекту или задаче на участке."),
    ("Опт и регулярные отгрузки", "Работаем с подрядчиками: договор, НДС, отсрочка при повторных заказах."),
    ("Распил и строгание", "Пилим под размер, строгаем, пакуем перед отгрузкой."),
    ("Считаем кубатуру", "Пришлите чертёж или размеры — соберём спецификацию и цену."),
]

DEFAULT_STEPS = [
    ("Заявка", "на сайте или по телефону"),
    ("Согласование", "объёма и размеров"),
    ("Подтверждение", "заказа"),
    ("Подготовка", "материалов на складе"),
    ("Доставка", "или самовывоз"),
]

DEFAULT_SERVICES = [
    ("Доставка на объект", "Манипулятором по Екатеринбургу и Свердловской области."),
    ("Распил по размерам", "Под сечение из спецификации, без лишней кубатуры."),
    ("Оптовые поставки", "Регулярные отгрузки для подрядчиков и строительных баз."),
    ("Помощь в подборе материалов", "Порода, сорт и влажность — под задачу на объекте."),
]

DEFAULT_APPLICATIONS = [
    ("Строительство домов", "Каркас, стены и перекрытия из бруса и обрезной доски.", "Обрезной брус, Обрезная доска, Брусок"),
    ("Бани и сауны", "Вагонка, половая доска и брус для сруба.", "Вагонка, Половая доска, Строганный брус"),
    ("Кровля и перекрытия", "Стропильная система, обрешётка и контробрешётка.", "Обрезной брус, Обрезная доска"),
    ("Беседки и благоустройство", "Террасы, ограждения и садовые настилы.", "Строганная доска, Брусок"),
]

DEFAULT_FAQ = [
    ("Какой минимальный заказ?", "Со склада от 1 м³. Погонаж и вагонку можно заказать от 10 м²."),
    ("Куда возите и сколько едет?", "По Екатеринбургу и Свердловской области. Если позиция на складе — отгрузка в день заказа."),
    ("Естественная влажность или камерная сушка?", "Естественная (18–22%) дешевле — на черновые работы. Камерная (8–16%) держит геометрию — для полов и отделки."),
    ("Можно нестандартный размер?", "Да. Пилим, строгаем и сушим под сечение. Нестандарт обычно 2–5 рабочих дней."),
    ("Как посчитать объём?", "Пришлите проект, чертёж или размеры — соберём спецификацию и назовём цену."),
    ("Как оплатить?", "Карта, СБП, наличные при получении или счёт для юрлица. Для организаций — договор поставки."),
]


class Command(BaseCommand):
    help = "Первичная настройка: суперпользователь, категории, контакты и стартовый контент."

    def add_arguments(self, parser):
        parser.add_argument("--username", default="admin", help="Логин администратора (по умолчанию: admin)")
        parser.add_argument("--password", default="UralForest2026!", help="Пароль администратора")
        parser.add_argument("--email", default="Ural_forest@bk.ru", help="E-mail администратора")
        parser.add_argument("--with-demo", action="store_true", help="Добавить демонстрационные товары")

    @transaction.atomic
    def handle(self, *args, **options):
        self._create_superuser(options)
        self._site_settings(options)
        self._categories()
        self._content()
        if options["with_demo"]:
            self._demo_products()
        self.stdout.write(self.style.SUCCESS("\nГотово! Сайт настроен и готов к наполнению."))

    def _create_superuser(self, options):
        User = get_user_model()
        username = options["username"]
        if User.objects.filter(username=username).exists():
            self.stdout.write(f"  · Пользователь «{username}» уже существует — пропускаю.")
            return
        User.objects.create_superuser(username=username, email=options["email"], password=options["password"])
        self.stdout.write(self.style.SUCCESS(f"  · Создан суперпользователь «{username}»."))
        self.stdout.write(f"    Логин: {username}")
        self.stdout.write(f"    Пароль: {options['password']}")
        self.stdout.write(self.style.WARNING("    Смените пароль после первого входа в админку!"))

    def _site_settings(self, options):
        site = SiteSettings.load()
        site.company_name = 'ООО ТПК «Уральский лес»'
        site.short_name = "Уральский лес"
        site.email = options["email"]
        site.phone1 = "+7 (343) 200-77-74"
        site.phone2 = "+7 (950) 202-19-33"
        site.whatsapp = "+79502021933"
        site.address = "г. Екатеринбург"
        site.work_hours = "Ежедневно с 9:00 до 20:00"
        site.meta_title = 'Пиломатериалы в Екатеринбурге — ООО ТПК «Уральский лес»'
        site.meta_description = "Пиломатериалы от производителя в Екатеринбурге: доска, брус, вагонка. Доставка по городу и Свердловской области."
        site.save()
        self.stdout.write("  · Настройки сайта обновлены.")

    def _categories(self):
        for order, (name, short) in enumerate(DEFAULT_CATEGORIES):
            Category.objects.update_or_create(
                name=name,
                defaults={"short_description": short, "order": order, "is_active": True},
            )
        self.stdout.write(f"  · Категорий в каталоге: {Category.objects.count()}")

    def _content(self):
        if not Advantage.objects.exists():
            for i, (title, text) in enumerate(DEFAULT_ADVANTAGES):
                Advantage.objects.create(title=title, text=text, order=i)
        if not WorkStep.objects.exists():
            for i, (title, text) in enumerate(DEFAULT_STEPS):
                WorkStep.objects.create(title=title, text=text, order=i)
        if not Service.objects.exists():
            for i, (title, text) in enumerate(DEFAULT_SERVICES):
                Service.objects.create(title=title, text=text, order=i)
        if not Application.objects.exists():
            for i, (title, text, tags) in enumerate(DEFAULT_APPLICATIONS):
                Application.objects.create(title=title, text=text, tags=tags, order=i)
        if not FAQ.objects.exists():
            for i, (q, a) in enumerate(DEFAULT_FAQ):
                FAQ.objects.create(question=q, answer=a, order=i)
        self.stdout.write("  · Стартовый контент (преимущества, услуги, этапы, применение, FAQ) добавлен.")

    def _demo_products(self):
        from decimal import Decimal

        cats = {c.name: c for c in Category.objects.all()}
        demo = [
            ("Пиломатериал естественной влажности", "Доска обрезная 25×150×6000", "m3", "16500", "25×150×6000", "Сосна", "АВ", "18–22%", "44"),
            ("Пиломатериал естественной влажности", "Брус обрезной 100×100×6000", "m3", "16500", "100×100×6000", "Сосна", "АВ", "18–22%", "16"),
            ("Пиломатериал камерной сушки", "Доска обрезная 50×150×6000 сухая", "m3", "22000", "50×150×6000", "Сосна", "АВ", "8–16%", "22"),
            ("Пиломатериал строганный, камерной сушки", "Доска строганная 20×140×3000", "pcs", "375", "20×140×3000", "Сосна", "АВ", "8–12%", ""),
            ("Пиломатериал строганный, камерной сушки", "Вагонка штиль", "m2", "500", "12,5×96×3000", "Осина", "АВ", "8–12%", ""),
            ("Пиломатериал антисептированный", "Брусок антисептированный 50×50×3000", "pcs", "250", "50×50×3000", "Сосна", "В", "18–22%", ""),
            ("Деревянные дома, беседки", "Беседка деревянная 3×3 м", "pcs", "85000", "3000×3000", "Сосна", "", "18–22%", ""),
        ]
        created = 0
        for cat_name, name, unit, price, size, wood, grade, moisture, per_cube in demo:
            cat = cats.get(cat_name)
            if not cat:
                continue
            Product.objects.get_or_create(
                name=name,
                category=cat,
                defaults={
                    "unit": unit,
                    "price": Decimal(price),
                    "size": size,
                    "wood_type": wood,
                    "grade": grade,
                    "moisture": moisture,
                    "per_cube": per_cube,
                    "is_featured": created < 4,
                },
            )
            created += 1
        self.stdout.write(f"  · Добавлено демонстрационных товаров: {created}")
