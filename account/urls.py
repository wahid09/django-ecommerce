from django.contrib import admin
from django.urls import path, include
from . import views

app_name='account'

urlpatterns = [
    path('register/', views.get_register, name='register'),
    path('login', views.get_login, name='login'),
    path('logout/', views.get_logout, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('', views.dashboard, name='dashboard'),

    path('activate/<uidb64>/<token>/', views.activate, name='activate'),
]