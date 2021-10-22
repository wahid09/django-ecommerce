from django.shortcuts import render, HttpResponse, HttpResponseRedirect
from store.models import Product

def home(request):
    products = Product.objects.all().filter(is_available=True)
    context = {
        'products': products,
    }
    return render(request, 'master/home.html', context)
