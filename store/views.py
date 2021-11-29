from django.shortcuts import render, get_object_or_404, redirect
from .models import Product, ReviewRating
from category.models import Category
from cart.models import CartItem
from cart.views import _cart_id
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.http import HttpResponse
from django.db.models import Q
from .forms import ReviewFroms
from django.contrib import messages
from order.models import OrderProduct

# Create your views here.


def store(request, category_slug=None):
    categories = None
    products = None

    if category_slug != None:
        categories = get_object_or_404(Category, slug=category_slug)
        products = Product.objects.filter(category=categories, is_available=True).order_by('id')
        paginator = Paginator(products, 12)
        page_number = request.GET.get('page')
        paged_products = paginator.get_page(page_number)
        product_count = products.count()
    else:
        products = Product.objects.all().filter(is_available=True).order_by('id')
        paginator = Paginator(products, 12)
        page_number = request.GET.get('page')
        paged_products = paginator.get_page(page_number)
        product_count = products.count()
    context = {
        'products': paged_products,
        'product_count': product_count,
    }
    return render(request, 'store/store.html', context)


def product_detail(request, category_slug=None, product_slug=None):
    try:
        single_product = Product.objects.get(category__slug=category_slug, slug=product_slug)
        print(single_product.avarageReview)
        in_cart = CartItem.objects.filter(cart__cart_id=_cart_id(request), product=single_product).exists()
    except Exception as e:
        raise e
    if request.user.is_authenticated:
        try:
            order_product = OrderProduct.objects.filter(user=request.user, product_id=single_product).exists()
        except order_product.DoesNotExist:
            order_product = None
    else:
        order_product = None

    reviews = ReviewRating.objects.filter(product_id=single_product.id, status=True)

    context = {
        'single_product': single_product,
        'in_cart': in_cart,
        'order_product': order_product,
        'reviews': reviews,
    }
    return render(request, 'store/product_detail.html', context)


def product_search(request):
    if 'keyword' in request.GET:
        keyword = request.GET['keyword']
        if keyword:
            products = Product.objects.filter(is_available=True).order_by('-created_at')
            products = products.filter(
                Q(product_name__icontains=keyword) |
                Q(description__icontains=keyword)
            )
    paginator = Paginator(products, 12)
    page_number = request.GET.get('page')
    paged_products = paginator.get_page(page_number)
    product_count = products.count()
    context = {
        'products': paged_products,
        'product_count': product_count
    }
    return render(request, 'store/store.html', context)


def submit_review(request, product_id):
    url = request.META.get("HTTP_REFERER")
    if request.method == "POST":
        try:
            reviews = ReviewRating.objects.get(user__id=request.user.id, product__id=product_id)
            form = ReviewFroms(request.POST, isinstance=reviews)
            form.save()
            messages.success(request, f"Your review has been updated!")
            return redirect(url)
        except ReviewRating.DoesNotExist:
            form = ReviewFroms(request.POST)
            if form.is_valid():
                data = ReviewRating()
                data.subject = form.cleaned_data['subject']
                data.rating = form.cleaned_data['rating']
                data.review = form.cleaned_data['review']
                data.ip = request.META.get('REMOTE_ADDR')
                data.product_id = product_id
                data.user_id = request.user.id
                data.save()
                messages.success(request, f"Your review has been submitted!")
                return redirect(url)

