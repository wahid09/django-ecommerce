from django.shortcuts import render, redirect
from django.http import HttpResponse
from .forms import RegistrationFrom
from .models import Account
from django.contrib import messages

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
            messages.success(request, 'Registration successfull')
            return redirect('account:register')
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
    return render(request, 'account/login.html')

def get_logout(request):
    pass
