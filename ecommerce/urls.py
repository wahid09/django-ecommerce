from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('store/', include('store.urls')),
    path('cart/', include('cart.urls')),
    path('account/', include('account.urls')),
    path('order/', include('order.urls'))
]+static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


admin.site.site_header = 'GreatKart Administration'
