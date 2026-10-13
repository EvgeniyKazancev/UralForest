from django.urls import path

from . import views

app_name = "catalog"

urlpatterns = [
    path("", views.catalog_list, name="list"),
    path("category/<slug:slug>/", views.category_detail, name="category"),
    path("<slug:slug>/", views.product_detail, name="product"),
]
