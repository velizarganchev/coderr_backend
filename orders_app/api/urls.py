from django.urls import path

from .views import Orders_View, SingleOrder_View, NotCompletedOrderCount_View, CompletedOrderCount_View

urlpatterns = [
    path('api/orders/', Orders_View.as_view(), name='orders'),
    path('api/orders/<pk>/', SingleOrder_View.as_view(), name='single_order'),
    path('api/order-count/<pk>/',
         NotCompletedOrderCount_View.as_view(), name='not_completed_order'),
    path('api/completed-order-count/<pk>/',
         CompletedOrderCount_View.as_view(), name='completed_order'),
]
