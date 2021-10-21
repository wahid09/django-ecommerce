from django.contrib import admin
from .models import Category

# Register your models here.


class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('category_name',)}
    list_display = ('category_name', 'created_at', 'is_active')


admin.site.register(Category, CategoryAdmin)



