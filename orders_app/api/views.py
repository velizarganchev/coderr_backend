from rest_framework import generics, status, permissions
from rest_framework.response import Response

from ..models import Order
from .serializers import OrderSerializer


class Orders_View(generics.ListCreateAPIView):
    """
    View to list and create orders.
    Only authenticated users can access this view.
    """
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = OrderSerializer

    def get_queryset(self):
        """
        Return the queryset of orders for the authenticated business user.
        """
        user = self.request.user
        return Order.objects.filter(business_user=user) | Order.objects.filter(customer_user=user)


class SingleOrder_View(generics.RetrieveUpdateDestroyAPIView):
    """
    View to retrieve, update, or delete a single order.
    Only authenticated users can access this view.
    """
    permission_classes = [permissions.IsAuthenticated]
    queryset = Order.objects.all()
    serializer_class = OrderSerializer


class NotCompletedOrderCount_View(generics.ListAPIView):
    """
    View to get the count of not completed orders.
    Only authenticated users can access this view.
    """
    permission_classes = [permissions.IsAuthenticated]
    queryset = Order.objects.all()
    serializer_class = OrderSerializer

    def get(self, request, pk, format=None):
        """
        Return the count of orders with status 'in_progress' or 'cancelled'.
        """
        order_count = Order.objects.filter(
            status__in=['in_progress', 'cancelled']).count()
        return Response({'order_coun': order_count}, status=status.HTTP_200_OK)


class CompletedOrderCount_View(generics.ListAPIView):
    """
    View to get the count of completed orders.
    Only authenticated users can access this view.
    """
    permission_classes = [permissions.IsAuthenticated]
    queryset = Order.objects.all()
    serializer_class = OrderSerializer

    def get(self, request, pk, format=None):
        """
        Return the count of orders with status 'completed'.
        """
        order_count = Order.objects.filter(
            status__in=['completed']).count()
        return Response({'completed_order_count': order_count}, status=status.HTTP_200_OK)
