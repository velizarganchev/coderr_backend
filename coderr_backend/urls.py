from django.contrib import admin
from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static

from .api.views import BaseInfo_View

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/base-info/', BaseInfo_View.as_view(), name='base_info'),
    path('', include('offers_app.api.urls')),
    path('', include('user_auth_app.api.urls')),
    path('', include('orders_app.api.urls')),
    path('', include('reviews_app.api.urls')),
    # Temporarily comment out the catch-all pattern
    # path('^(?P<path>.*)$', include('django.views.static.serve')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
