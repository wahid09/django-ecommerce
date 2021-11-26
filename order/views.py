from django.shortcuts import render, redirect, HttpResponseRedirect
from cart.models import CartItem
from .forms import OrderForm
from .models import Order, Payment, OrderProduct
import datetime
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages

# for payment

import requests
from sslcommerz_python.payment import SSLCSession
from decimal import Decimal
import socket

# Create your views here.

@login_required
def place_order(request, total=0, quantity=0):
    current_user = request.user
    cart_items = CartItem.objects.filter(user=current_user)
    cart_count = cart_items.count()
    if cart_count <= 0:
        return redirect('store:store')

    grant_total = 0
    tax = 0

    for cart_item in cart_items:
        total = (cart_item.product.price * cart_item.quantity)
        quantity += cart_item.quantity
    tax = (4*total)/100
    grant_total = total + tax

    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            data = Order()
            data.user = current_user
            data.first_name = form.cleaned_data['first_name']
            data.last_name = form.cleaned_data['last_name']
            data.phone_number = form.cleaned_data['phone_number']
            data.email = form.cleaned_data['email']
            data.address_line_1 = form.cleaned_data['address_line_1']
            data.address_line_2 = form.cleaned_data['address_line_2']
            data.country = form.cleaned_data['country']
            data.state = form.cleaned_data['state']
            data.city = form.cleaned_data['city']
            data.order_note = form.cleaned_data['order_note']
            data.order_total = grant_total
            data.tax = tax
            data.ip = request.META.get('REMOTE_ADDR')
            data.save()

            # generate order number
            yr = int(datetime.date.today().strftime('%Y'))
            dt = int(datetime.date.today().strftime('%d'))
            mt = int(datetime.date.today().strftime('%m'))
            d = datetime.date(yr,mt,dt)
            current_date = d.strftime("%Y%m%d")

            order_number =  current_date + str(data.id)
            data.order_number = order_number
            data.save()

            order = Order.objects.get(user=current_user, is_ordered=False, order_number=order_number)
            context = {
                'order': order,
                'cart_items': cart_items,
                'total': total,
                'tax': tax,
                'grant_total': grant_total,
                'order_number': order_number,
            }
            #print(grant_total)

            #return render(request, 'order/payment.html', context)
            return redirect('order:payment')
    else:
        return redirect('cart:checkout')

@login_required
def payment(request, total=0, quantity=0):
    current_user = request.user
    cart_items = CartItem.objects.filter(user=current_user)
    cart_count = cart_items.count()
    if cart_count <= 0:
        return redirect('store:store')

    grant_total = 0
    tax = 0

    for cart_item in cart_items:
        total = (cart_item.product.price * cart_item.quantity)
        quantity += cart_item.quantity
    tax = (4 * total) / 100
    grant_total = total + tax
    order = Order.objects.filter(user=current_user, is_ordered=False)
    order = order[0]
    context = {
        'order': order,
        'cart_items': cart_items,
        'total': total,
        'tax': tax,
        'grant_total': grant_total,
    }

    return render(request, 'order/payment.html', context)

@login_required
def make_payment(request, total=0, quantity=0):
    current_user = request.user
    cart_items = CartItem.objects.filter(user=current_user)
    cart_count = cart_items.count()
    if cart_count <= 0:
        return redirect('store:store')

    grant_total = 0
    tax = 0

    for cart_item in cart_items:
        total = (cart_item.product.price * cart_item.quantity)
        quantity += cart_item.quantity
    tax = (4 * total) / 100
    grant_total = total + tax
    order = Order.objects.filter(user=current_user, is_ordered=False)
    order = order[0]
    context = {
        'order': order,
        'cart_items': cart_items,
        'total': total,
        'tax': tax,
        'grant_total': grant_total,
    }
    store_id = 'abc61a06c6d5a242'
    store_passcode = 'abc61a06c6d5a242@ssl'

    mypayment = SSLCSession(sslc_is_sandbox=True, sslc_store_id=store_id,
                            sslc_store_pass=store_passcode)

    status_url = request.build_absolute_uri(reverse("order:payment_status"))
    mypayment.set_urls(success_url=status_url, fail_url=status_url,
                       cancel_url=status_url, ipn_url=status_url)

    mypayment.set_product_integration(total_amount=Decimal(grant_total), currency='BDT', product_category='clothing',
                                      product_name='demo-product', num_of_item=quantity, shipping_method='YES',
                                      product_profile='None')

    mypayment.set_customer_info(name=order.full_name, email=order.email, address1=order.full_address,
                                address2='demo address 2', city=order.city, postcode=order.state, country=order.country,
                                phone=order.phone_number)

    mypayment.set_shipping_info(shipping_to=order.full_name, address=order.full_address, city=order.city,
                                postcode=order.state,
                                country=order.country)
    response_data = mypayment.init_payment()
    if response_data:
        return redirect(response_data['GatewayPageURL'])
    else:
        return redirect('order:payment')


@csrf_exempt
def complete(request):
    if request.method == "POST" or request.method == "post":
        payment_data = request.POST
        status = payment_data['status']
        tran_id = payment_data['tran_id']
        store_amount = payment_data['store_amount']
        card_type = payment_data['card_type']
        # order = Order.objects.filter(user=request.user, is_ordered=False)

        if status == 'VALID':
            # payment = Payment(
            #     #user=order_user.user,
            #     payment_id=tran_id,
            #     amount_paid=store_amount,
            #     payment_method=card_type,
            #     status=status
            # )
            # payment.save()
            #
            # order.payment = payment
            # order.is_ordered = True
            # order.save()

            messages.success(request, f'Your Payment Completed Successfully' + tran_id)
            # return redirect('store:store')
            return HttpResponseRedirect(reverse("order:purchase", kwargs={'tran_id':tran_id, 'store_amount':store_amount, 'card_type': card_type, 'status': status}))
        elif status == 'FAILED':
            messages.warning(request, f'Your Payment Failed! Please Try Again')

    return render(request, 'order/order_complete.html')


@login_required
def purchase(request, tran_id, card_type, store_amount, status):
    order = Order.objects.filter(user=request.user, is_ordered=False)
    order = order[0]
    payment = Payment(
        user=request.user,
        payment_id=tran_id,
        amount_paid=store_amount,
        payment_method=card_type,
        status=status
    )
    payment.save()

    order.payment = payment
    order.is_ordered = True
    order.save()

    # remove the cart item
    cart_item = CartItem.objects.filter(user=request.user)
    for item in cart_item:
        order_product = OrderProduct()
        order_product.order_id = order.id
        order_product.payment = payment
        order_product.user_id = request.user.id
        order_product.product_id = item.product_id
        order_product.quantity = item.quantity
        order_product.product_price = item.product.price
        order_product.ordered = True
        order_product.save()
    return HttpResponseRedirect(reverse('home'))





