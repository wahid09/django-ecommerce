from .models import Category


def manu_links(request):
    links = Category.objects.all().filter(is_active=True)
    return dict(links=links)


