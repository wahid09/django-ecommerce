from django.contrib import admin
from .models import Product, Variation, ReviewRating

# Register your models here.


class VariationInline(admin.TabularInline):
    model = Variation
    readonly_fields = ('product', 'variation_category', 'variation_value', 'is_active')
    extra = 0


class ProductAdmin(admin.ModelAdmin):
    list_display = ('product_name', 'category', 'price', 'stock', 'updated_at', 'is_available')
    prepopulated_fields = {'slug': ('product_name',)}
    list_editable = ['is_available', 'stock']
    search_fields = ['product_name', 'category', 'price']
    list_filter = ['category', 'price', 'stock']
    list_per_page = 20
    inlines = [VariationInline]


admin.site.register(Product, ProductAdmin)


class VariationAdmin(admin.ModelAdmin):
    list_display = ('product', 'variation_category', 'variation_value', 'is_active')
    list_editable = ('is_active',)
    list_filter = ('product', 'variation_category', 'variation_value', 'is_active')
    list_per_page = 20


admin.site.register(Variation, VariationAdmin)


class ReviewRatingAdmin(admin.ModelAdmin):
    list_display = ['product', 'subject', 'review', 'rating', 'created_at', 'status']
    list_editable = ['rating', 'status']
    list_filter = ['rating', 'status']


admin.site.register(ReviewRating, ReviewRatingAdmin)