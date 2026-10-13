from .models import SiteSettings


def site_context(request):
    """Делает настройки сайта и корзину доступными во всех шаблонах."""
    from cart.cart import Cart
    from catalog.models import Category

    return {
        "site": SiteSettings.load(),
        "cart": Cart(request),
        "nav_categories": Category.objects.filter(is_active=True),
    }
