from django.shortcuts import render, redirect, HttpResponseRedirect
from django.http import HttpResponse
from .forms import RegistrationFrom
from .models import Account
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

            user = Account.objects.create_user(first_name=first_name, last_name=last_name, email=email, username=username, password=password)

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

            messages.success(request, f"Thank you for registering with us, We have sent you a verification email to your email address. Please verify it")
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
                auth.login(request, user)
                #messages.success(request, 'You are now logged in.')
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
    return render(request, 'account/dashboard.html')

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

