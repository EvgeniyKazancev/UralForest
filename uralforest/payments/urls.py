from django.urls import path

from . import views

app_name = "payments"

urlpatterns = [
    path("start/<str:order_number>/", views.start, name="start"),
    path("mock/<str:order_number>/", views.mock_confirm, name="mock_confirm"),
    path("mock/<str:order_number>/pay/", views.mock_pay, name="mock_pay"),
    path("mock/<str:order_number>/cancel/", views.mock_cancel, name="mock_cancel"),
    path("return/<str:order_number>/", views.return_view, name="return"),
    path("webhook/", views.webhook, name="webhook"),
]
