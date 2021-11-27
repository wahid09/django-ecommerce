from django.urls import path
from . import views


app_name = 'order'


urlpatterns = [
    path('place-order', views.place_order, name='place_order'),
    path('payments', views.payment, name='payment'),
    path('pay/', views.make_payment, name='make_payment'),
    path('payment-status/', views.complete, name='payment_status'),
    path('purchase/<tran_id>/<card_type>/<store_amount>/<status>/', views.purchase, name='purchase'),
    path('order-complete/<order_number>/', views.order_complete, name='order_complete')
]