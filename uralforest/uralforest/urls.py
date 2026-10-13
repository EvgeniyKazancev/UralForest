from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path, re_path
from django.views.static import serve as media_serve

admin.site.site_header = "ООО ТПК «Уральский лес» — панель управления"
admin.site.site_title = "Уральский лес"
admin.site.index_title = "Управление сайтом"

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("core.urls")),
    path("catalog/", include("catalog.urls")),
    path("cart/", include("cart.urls")),
    path("orders/", include("orders.urls")),
    path("payments/", include("payments.urls")),
    # Раздача загруженных файлов (фото товаров, логотип) — работает и в контейнере
    re_path(r"^media/(?P<path>.*)$", media_serve, {"document_root": settings.MEDIA_ROOT}),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.BASE_DIR / "static")

