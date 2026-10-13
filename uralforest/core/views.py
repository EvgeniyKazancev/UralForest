from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.views.decorators.http import require_POST

from catalog.models import Category, Product

from .forms import LeadForm
from .models import (
    Advantage,
    Application,
    FAQ,
    LeadRequest,
    Review,
    Service,
    WorkStep,
)


def home(request):
    context = {
        "categories": Category.objects.filter(is_active=True),
        "featured_products": Product.objects.filter(is_active=True, is_featured=True)[:8],
        "products": Product.objects.filter(is_active=True)[:8],
        "services": Service.objects.filter(is_active=True),
        "advantages": Advantage.objects.filter(is_active=True),
        "work_steps": WorkStep.objects.filter(is_active=True),
        "applications": Application.objects.filter(is_active=True),
        "reviews": Review.objects.filter(is_published=True)[:6],
        "faqs": FAQ.objects.filter(is_active=True),
        "lead_form": LeadForm(),
    }
    return render(request, "core/home.html", context)


@require_POST
def lead_create(request):
    form = LeadForm(request.POST)
    is_ajax = request.headers.get("x-requested-with") == "XMLHttpRequest"
    if form.is_valid():
        lead = form.save()
        _notify_managers(lead)
        message = "Спасибо! Заявка отправлена — мы свяжемся с вами в ближайшее время."
        if is_ajax:
            return JsonResponse({"ok": True, "message": message})
        messages.success(request, message)
    else:
        if is_ajax:
            return JsonResponse({"ok": False, "errors": form.errors}, status=400)
        messages.error(request, "Проверьте правильность заполнения формы.")
    return redirect(request.META.get("HTTP_REFERER", "/"))


def _notify_managers(lead: LeadRequest):
    subject = f"Новая заявка с сайта: {lead.get_kind_display()}"
    body = (
        f"Тип: {lead.get_kind_display()}\n"
        f"Имя: {lead.name}\n"
        f"Телефон: {lead.phone}\n"
        f"E-mail: {lead.email or '—'}\n"
        f"Материал/объём: {lead.material or '—'}\n"
        f"Способ связи: {lead.get_contact_method_display()}\n"
        f"Сообщение: {lead.message or '—'}\n"
    )
    try:
        send_mail(subject, body, settings.DEFAULT_FROM_EMAIL, [settings.ORDERS_NOTIFY_EMAIL], fail_silently=True)
    except Exception:  # noqa: BLE001
        pass


def privacy(request):
    return render(request, "core/privacy.html")


def personal_data(request):
    return render(request, "core/personal_data.html")


def offer(request):
    return render(request, "core/offer.html")


def contacts(request):
    context = {"lead_form": LeadForm(initial={"kind": LeadRequest.Kind.CONTACT})}
    return render(request, "core/contacts.html", context)
