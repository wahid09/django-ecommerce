from django.contrib import admin
from django.urls import path, include
from . import views
from .views import MyOrderListView

app_name='account'

urlpatterns = [
    path('register/', views.get_register, name='register'),
    path('login', views.get_login, name='login'),
    path('logout/', views.get_logout, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('', views.dashboard, name='dashboard'),

    path('activate/<uidb64>/<token>/', views.activate, name='activate'),
    path('forgotPassword/', views.forgot_password, name='forgot_password'),
    path('reset_password_validate/<uidb64>/<token>/', views.reset_password_validate, name='reset_password_validate'),
    path('resetPassword/', views.reset_password, name='reset_password'),
    #path('my_orders/', views.my_orders, name='my_order'),
    path('my_orders/', MyOrderListView.as_view(), name='my_order'),
    path('edit_profile/', views.edit_profile, name='edit_profile'),
    path('change_password/', views.change_password, name='change_password'),
    path('order_details/<int:order_id>/', views.order_detail, name='order_detail'),
]