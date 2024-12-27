from rest_framework import generics, status, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied
from django.db.models import Q
from django.contrib.auth.models import User

from ..models import Order
from .serializers import OrderSerializer


class OrdersView(generics.ListCreateAPIView):
    """
    View to list and create orders.
    Only authenticated users can access this view.
    """
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = OrderSerializer

    def get_queryset(self):
        """
        Return the queryset of orders for the authenticated business user or customer.
        """
        user = self.request.user

        return Order.objects.filter(
            Q(business_user=user) | Q(customer_user=user)
        )


class SingleOrderView(generics.RetrieveUpdateDestroyAPIView):
    """
    View to retrieve, update, or delete a single order.
    Only authenticated users can access this view.
    """
    permission_classes = [permissions.IsAuthenticated]
    queryset = Order.objects.all()
    serializer_class = OrderSerializer

    def delete(self, request, pk):
        """
        Handle deletion of an order.
        """
        try:
            order = Order.objects.get(pk=pk)
        except Order.DoesNotExist:
            return Response(
                {"detail": "Bestellung nicht gefunden."},
                status=status.HTTP_404_NOT_FOUND
            )

        if not request.user.is_staff:
            raise PermissionDenied(
                {"detail": "Nur Mitarbeiter können Bestellungen löschen."}
            )

        order.delete()
        return Response(
            {"detail": "Bestellung erfolgreich gelöscht."},
            status=status.HTTP_204_NO_CONTENT
        )


class NotCompletedOrderCountView(APIView):
    """
    View to get the count of not completed orders (status: 'in_progress') for a specific user.
    Only authenticated users can access this view.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pk, format=None):
        """
        Return the count of orders with status 'in_progress' for the user identified by `pk`.
        """

        try:
            user = User.objects.get(pk=pk)
        except User.DoesNotExist:
            return Response(
                {"error": "Geschäftsbenutzer nicht gefunden."},
                status=status.HTTP_404_NOT_FOUND
            )

        if not request.user and str(request.user.pk) != str(pk):
            return Response(
                {"detail": "Sie können nur Bestellungen für Ihr eigenes Konto abrufen."},
                status=status.HTTP_403_FORBIDDEN
            )

        order_count = Order.objects.filter(
            Q(status='in_progress'),
            Q(business_user=user) | Q(customer_user=user)
        ).count()

        return Response({'order_count': order_count}, status=status.HTTP_200_OK)


class CompletedOrderCountView(APIView):
    """
    View to get the count of completed or cancelled orders for a specific user.
    Only authenticated users can access this view.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pk, format=None):
        """
        Return the count of orders with status 'completed' or 'cancelled'
        for the user identified by `pk`.
        """

        try:
            user = User.objects.get(pk=pk)
        except User.DoesNotExist:
            return Response(
                {"error": "Geschäftsbenutzer nicht gefunden."},
                status=status.HTTP_404_NOT_FOUND
            )

        if not request.user and str(request.user.pk) != str(pk):
            return Response(
                {"detail": "Sie können nur Bestellungen für Ihr eigenes Konto abrufen."},
                status=status.HTTP_403_FORBIDDEN
            )

        completed_order_count = Order.objects.filter(
            Q(status__in=['completed', 'cancelled']),
            Q(business_user=user) | Q(customer_user=user)
        ).count()

        return Response({'completed_order_count': completed_order_count}, status=status.HTTP_200_OK)
