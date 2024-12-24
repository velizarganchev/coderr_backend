from django.urls import path
"""
URL configuration for the orders_app API.
This module defines the URL patterns for the orders_app API, mapping URLs to their corresponding views.
Routes:
- 'api/orders/': Maps to Orders_View, which handles requests related to all orders.
- 'api/orders/<pk>/': Maps to SingleOrder_View, which handles requests related to a single order identified by its primary key (pk).
- 'api/order-count/<pk>/': Maps to NotCompletedOrderCount_View, which handles requests to get the count of not completed orders for a specific user identified by their primary key (pk).
- 'api/completed-order-count/<pk>/': Maps to CompletedOrderCount_View, which handles requests to get the count of completed orders for a specific user identified by their primary key (pk).
"""

from .views import Orders_View, SingleOrder_View, NotCompletedOrderCount_View, CompletedOrderCount_View

urlpatterns = [
    path('api/orders/', Orders_View.as_view(), name='orders'),
    path('api/orders/<pk>/', SingleOrder_View.as_view(), name='single_order'),
    path('api/order-count/<pk>/',
         NotCompletedOrderCount_View.as_view(), name='not_completed_order'),
    path('api/completed-order-count/<pk>/',
         CompletedOrderCount_View.as_view(), name='completed_order'),
]
