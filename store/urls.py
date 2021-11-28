from django.urls import path
from . import views


app_name = 'store'


urlpatterns = [
    path('', views.store, name='store'),
    path('category/<slug:category_slug>/', views.store, name='products_by_category'),
    path('product-details/<slug:category_slug>/<slug:product_slug>/', views.product_detail, name='product_detail'),
    path('search/', views.product_search, name='product_search'),
    path('submit-review/<product_id>/', views.submit_review, name='submit_review')
]