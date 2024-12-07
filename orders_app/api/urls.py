from django.urls import path

from .views import Orders_View, SingleOrder_View

urlpatterns = [
    path('api/orders/', Orders_View.as_view(), name='orders'),
    path('api/orders/<pk>/', SingleOrder_View.as_view(), name='single_order'),
]
