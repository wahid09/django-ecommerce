from django.contrib import admin
from .models import Payment, Order, OrderProduct

# Register your models here.


class OrderProductInline(admin.TabularInline):
    model = OrderProduct
    readonly_fields = ('payment', 'user', 'product', 'quantity', 'product_price', 'ordered')
    extra = 0


class OrderAdmin(admin.ModelAdmin):
    list_display = ['order_number', 'full_name', 'phone_number', 'email', 'city', 'state', 'country', 'order_total', 'created_at', 'status']
    list_editable = ['status']
    list_filter = ['status', 'is_ordered']
    search_fields = ['order_number', 'first_name', 'last_name', 'phone_number', 'email']
    list_per_page = 20
    inlines = [OrderProductInline]


admin.site.register(Order, OrderAdmin)


class OrderProductAdmin(admin.ModelAdmin):
    list_display = ['payment', 'product', 'quantity', 'product_price', 'ordered', 'created_at']
    list_filter = ['ordered', 'created_at']
    search_fields = ['product', 'product_price', 'created_at']
    list_per_page = 20


admin.site.register(OrderProduct, OrderProductAdmin)


class PamentAdmin(admin.ModelAdmin):
    list_display = ['payment_id', 'payment_method', 'amount_paid', 'status', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['payment_method', 'amount_paid', 'payment_id']
    list_per_page = 20


admin.site.register(Payment, PamentAdmin)

