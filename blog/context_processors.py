from .models import Category


def site_categories(request):
    """Expose categories to all templates as `site_categories`."""
    try:
        cats = Category.objects.all()
    except Exception:
        cats = []
    return {"site_categories": cats}
