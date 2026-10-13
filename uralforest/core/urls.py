from django.urls import path

from . import views

app_name = "core"

urlpatterns = [
    path("", views.home, name="home"),
    path("lead/", views.lead_create, name="lead"),
    path("contacts/", views.contacts, name="contacts"),
    path("privacy/", views.privacy, name="privacy"),
    path("personal-data/", views.personal_data, name="personal_data"),
    path("offer/", views.offer, name="offer"),
]
