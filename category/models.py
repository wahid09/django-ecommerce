from django.db import models

# Create your models here.


class Category(models.Model):
    category_name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=264, unique=True)
    description = models.TextField(max_length=1200, blank=True)
    category_image = models.ImageField(upload_to='images/category', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'category'
        verbose_name_plural = 'caregories'


    def __str__(self):
        return self.category_name
