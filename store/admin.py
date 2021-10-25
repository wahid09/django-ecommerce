from django.contrib import admin
from .models import Product, Variation

# Register your models here.


class ProductAdmin(admin.ModelAdmin):
    list_display = ('product_name', 'category', 'price', 'stock', 'updated_at', 'is_available')
    prepopulated_fields = {'slug': ('product_name',)}


admin.site.register(Product, ProductAdmin)

class VariationAdmin(admin.ModelAdmin):
    list_display = ('product', 'variation_category', 'variation_value', 'is_active')
    list_editable = ('is_active',)
    list_filter = ('product', 'variation_category', 'variation_value', 'is_active')
admin.site.register(Variation, VariationAdmin)
