from django.shortcuts import render, redirect, HttpResponseRedirect, get_object_or_404
from django.http import HttpResponse
from .forms import RegistrationFrom, UserForm, UserProfileForm
from .models import Account, UserProfile
from django.contrib import messages, auth
from django.contrib.auth import authenticate, login, logout
from django.urls import reverse
from django.contrib.auth.decorators import login_required
# verification email

from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage
## Cart
from cart.models import Cart, CartItem
from cart.views import _cart_id
from order.models import Order
from django.core.paginator import Paginator
from django.views.generic import ListView
from django.core.paginator import EmptyPage
from django.core.paginator import PageNotAnInteger


# Create your views here.


def get_register(request):
    if request.method == 'POST':
        form = RegistrationFrom(request.POST)
        if form.is_valid():
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            email = form.cleaned_data['email']
            phone_number = form.cleaned_data['phone_number']
            password = form.cleaned_data['password']
            username = email.split("@")[0]

            user = Account.objects.create_user(first_name=first_name, last_name=last_name, email=email,
                                               username=username, password=password)

            user.phone_number = phone_number

            user.save()

            # User Activation
            current_sit = get_current_site(request)
            mail_subject = "Please active your account"
            message = render_to_string('account/account_verification_email.html', {
                'user': user,
                'domain': current_sit,
                'uid': urlsafe_base64_encode(force_bytes(user.id)),
                'token': default_token_generator.make_token(user)
            })
            to_email = email
            send_email = EmailMessage(mail_subject, message, to=[to_email])
            send_email.send()

            messages.success(request,
                             f"Thank you for registering with us, We have sent you a verification email to your email address. Please verify it")
            return redirect('account:login')
        else:
            messages.error(request, 'Something went wrong!')
            return redirect('account:register')
    else:
        form = RegistrationFrom()
    context = {
        'form': form
    }
    return render(request, 'account/register.html', context)


def get_login(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect(reverse('home'))
    else:
        if request.method == 'POST':
            email = request.POST['email']
            password = request.POST['password']

            user = auth.authenticate(email=email, password=password)

            if user is not None:
                try:
                    cart = Cart.objects.get(cart_id=_cart_id(request))
                    is_cart_item_exist = CartItem.objects.filter(cart=cart).exists()

                    if is_cart_item_exist:
                        cart_item = CartItem.objects.filter(cart=cart)
                        # geting the product variation by cart id
                        product_variation = []
                        for item in cart_item:
                            variation = item.variations.all()
                            product_variation.append(list(variation))

                        # getting the cart item by user and product variation
                        cart_item = CartItem.objects.filter(user=user)
                        ex_var_list = []
                        id = []
                        for item in cart_item:
                            existing_variation = item.variations.all()
                            ex_var_list.append(list(existing_variation))
                            id.append(item.id)

                        for pr in product_variation:
                            if pr in ex_var_list:
                                index=ex_var_list.index(pr)
                                item_id = id[index]
                                item=CartItem.objects.get(id=item_id)
                                item.quantity += 1
                                item.user = user
                                item.save()
                            else:
                                cart_item = CartItem.objects.filter(cart=cart)
                                for item in cart_item:
                                    item.user = user
                                    item.save()
                except:
                    pass
                auth.login(request, user)
                # messages.success(request, 'You are now logged in.')
                return redirect('account:dashboard')
            else:
                messages.error(request, 'Invalid Login credentials')
                return redirect('account:login')
        return render(request, 'account/login.html')


@login_required
def get_logout(request):
    logout(request)
    messages.info(request, 'You are now loggout.')
    return HttpResponseRedirect(reverse('account:login'))


def activate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account._default_manager.get(pk=uid)
    except(TypeError, ValueError, OverflowError, Account.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        messages.info(request, f"Your account is activated")
        return redirect('account:login')
    else:
        messages.error(request, f"Invalid activation link")
        return redirect('account:register')


@login_required
def dashboard(request):
    orders = Order.objects.order_by('-created_at').filter(user_id = request.user.id, is_ordered=True)
    order_count = orders.count()
    context = {
        'order_count': order_count,
    }
    return render(request, 'account/dashboard.html', context)


def forgot_password(request):
    if request.method == 'POST':
        email = request.POST['email']
        if Account.objects.filter(email=email).exists():
            user = Account.objects.get(email__exact=email)

            # Reset password email
            current_sit = get_current_site(request)
            mail_subject = "Please reset your password"
            message = render_to_string('account/reset_password_email.html', {
                'user': user,
                'domain': current_sit,
                'uid': urlsafe_base64_encode(force_bytes(user.id)),
                'token': default_token_generator.make_token(user)
            })
            to_email = email
            send_email = EmailMessage(mail_subject, message, to=[to_email])
            send_email.send()

            messages.success(request, f"Password reset email has been sent your email address")
            return redirect('account:login')

        else:
            messages.error(request, f"Account does not exists")
            return redirect('account:forgot_password')

    return render(request, 'account/forgot_password.html')


def reset_password_validate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account._default_manager.get(pk=uid)
    except(TypeError, ValueError, OverflowError, Account.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        request.session['uid'] = uid
        messages.success(request, f"Please reset your password")
        return redirect('account:reset_password')
    else:
        messages.error(request, f"This link has been expired!")
        return redirect('account:forgot_password')


def reset_password(request):
    if request.method == 'POST':
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']

        if password == confirm_password:
            uid = request.session.get('uid')
            user = Account.objects.get(pk=uid)
            user.set_password(password)
            user.save()

            messages.success(request, f"Password reset successfully")
            return redirect('account:login')
        else:
            messages.error(request, f"Password do not match!")
            return redirect('account:reset_password')
    else:
        return render(request, 'account/reset_password.html')


def my_orders(request):
    orders = Order.objects.order_by('-created_at').filter(user_id = request.user.id, is_ordered=True)
    paginator = Paginator(orders, 5)  # Show 25 contacts per page.

    page_number = request.GET.get('page')
    orders = paginator.get_page(page_number)
    context = {
        'orders': orders,
    }
    return render(request, 'account/my_order.html', context)

class MyOrderListView(ListView):
    paginate_by = 5
    model = Order
    # context_object_name = 'orders'

    def get_context_data(self, **kwargs):
        context = super(MyOrderListView, self).get_context_data(**kwargs)
        orders = Order.objects.order_by('-created_at').filter(user_id = self.request.user.id, is_ordered=True)
        paginator = Paginator(orders, self.paginate_by)

        page = self.request.GET.get('page')

        try:
            orders = paginator.page(page)
        except PageNotAnInteger:
            orders = paginator.page(1)
        except EmptyPage:
            orders = paginator.page(paginator.num_pages)

        context['orders'] = orders
        return context
@login_required
def edit_profile(request):
    user_profile = get_object_or_404(UserProfile, user=request.user)
    if request.method == 'POST':
        user_form = UserForm(request.POST, instance = request.user)
        profile_form = UserProfileForm(request.POST, request.FILES, instance = user_profile)

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()

            messages.success(request, f"profile updated successfully")
    else:
        user_form = UserForm(instance=request.user)
        profile_form = UserProfileForm(instance = user_profile)
    context = {
        'user_form': user_form,
        'profile_form': profile_form,
        'user_profile': user_profile
    }

    return render(request, 'account/edit_profile.html', context)

@login_required
def change_password(request):
    if request.method == 'POST':
        curret_password = request.POST['current_password']
        new_password = request.POST['new_password']
        confirm_password = request.POST['confirm_password']

        user = Account.objects.get(username__exact=request.user.username)

        if new_password == confirm_password:
            success = user.check_password(curret_password)
            if success:
                user.set_password(new_password)
                user.save()
                #auth.logout(request)
                messages.success(request, f'Password updated successfully')
                return redirect('account:login')
            else:
                messages.error(request, f'Please enter valid old password')
                return redirect('account:change_password')
        else:
            messages.error(request, f'Password does not match!')
            return redirect('account:change_password')
    return render(request, 'account/change_password.html')


