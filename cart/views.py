from django.shortcuts import render, redirect, get_object_or_404
from store.models import Product
from cart.models import Cart, CartItem

# Create your views here.


# def _cart_id(request):
#     cart = request.session.session_key
#     if not cart:
#         cart = request.session.create()

def _cart_id(request):
    cart = request.session.session_key
    if not cart:
        request.session.create()  # it does not return anything. that is why `cart = request.session.create()` will not work
        cart = request.session.session_key
    return cart  # Ultimately return cart


def add_cart(request, product_id):
    product = Product.objects.get(id=product_id)    # get the product

    try:
        cart = Cart.objects.get(cart_id=_cart_id(request))
    except Cart.DoesNotExist:
        cart = Cart.objects.create(
            cart_id=_cart_id(request)
        )
        cart.save()

    try:
        cart_item = CartItem.objects.get(product=product, cart=cart)
        cart_item.quantity +=1
        cart_item.save()
    except CartItem.DoesNotExist:
        cart_item = CartItem.objects.create(
            product=product,
            quantity=1,
            cart=cart,
        )

        cart_item.save()
    return redirect('cart:cart')


def cart(request, total=0, quantity=0, cart_items=None):
    try:
        cart_obj = Cart.objects.get(cart_id=_cart_id(request))
        cart_items = CartItem.objects.filter(cart=cart_obj, is_active=True)
        for cart_item in cart_items:
            total += cart_item.product.price*cart_item.quantity
            quantity += cart_item.quantity
        tax = (4*total)/100
        grand_total = total+tax
    except Exception as e:
        pass

    context = {
        'total': total,
        'quantity': quantity,
        'cart_items': cart_items,
        'tax': tax,
        'grand_total': grand_total
    }
    return render(request, 'cart/cart.html', context)


def remove_cart(request, product_id):
    cart_obj = Cart.objects.get(cart_id=_cart_id(request))
    product = get_object_or_404(Product, id=product_id)
    cart_item = CartItem.objects.get(product=product, cart=cart_obj)
    if cart_item.quantity > 1:
        cart_item.quantity -= 1
        cart_item.save()
    else:
        cart_item.delete()
    return redirect('cart:cart')


def delete_cart_item(request, product_id):
    cart_obj = Cart.objects.get(cart_id=_cart_id(request))
    product = get_object_or_404(Product, id=product_id)
    cart_item = CartItem.objects.get(product=product, cart=cart_obj)

    cart_item.delete()
    return redirect('cart:cart')


