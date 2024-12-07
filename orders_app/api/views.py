from rest_framework import generics, status
from rest_framework.response import Response

from ..models import Order
from .serializers import OrderSerializer


class Orders_View(generics.ListCreateAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer

    # def get(self, request, format=None):
    #     user = request.user
    #     orders = Order.objects.all()
    #     orders = Order.objects.filter(
    #         models.Q(customer_user__user=user) | models.Q(
    #             business_user__user=user)
    #     )
    #     serializer = OrderSerializer(orders, many=True)
    #     return Response(serializer.data, status=status.HTTP_200_OK)


class SingleOrder_View(generics.RetrieveUpdateDestroyAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
