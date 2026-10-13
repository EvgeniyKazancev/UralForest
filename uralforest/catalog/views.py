from django.shortcuts import get_object_or_404, render

from .models import Category, Product


def _sort_products(qs, sort):
    mapping = {
        "price_asc": "price",
        "price_desc": "-price",
        "name_asc": "name",
        "name_desc": "-name",
        "new": "-created_at",
    }
    return qs.order_by(mapping.get(sort, "order"))


def catalog_list(request):
    products = Product.objects.filter(is_active=True).select_related("category")
    categories = Category.objects.filter(is_active=True)

    category_slug = request.GET.get("category")
    current_category = None
    if category_slug:
        current_category = categories.filter(slug=category_slug).first()
        if current_category:
            products = products.filter(category=current_category)

    query = request.GET.get("q", "").strip()
    if query:
        products = products.filter(name__icontains=query) | products.filter(size__icontains=query)

    sort = request.GET.get("sort", "")
    products = _sort_products(products, sort)

    context = {
        "products": products,
        "categories": categories,
        "current_category": current_category,
        "query": query,
        "sort": sort,
    }
    return render(request, "catalog/list.html", context)


def category_detail(request, slug):
    category = get_object_or_404(Category, slug=slug, is_active=True)
    products = _sort_products(
        category.products.filter(is_active=True), request.GET.get("sort", "")
    )
    context = {
        "category": category,
        "categories": Category.objects.filter(is_active=True),
        "products": products,
    }
    return render(request, "catalog/category.html", context)


def product_detail(request, slug):
    product = get_object_or_404(
        Product.objects.select_related("category"), slug=slug, is_active=True
    )
    related = (
        Product.objects.filter(is_active=True, category=product.category)
        .exclude(pk=product.pk)[:4]
    )
    context = {
        "product": product,
        "related": related,
    }
    return render(request, "catalog/product.html", context)
