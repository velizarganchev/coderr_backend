from rest_framework import generics
from rest_framework.response import Response

from django.db.models import Q

from .serializers import OfferSerializer, OfferDetailSerializer
from ..models import Offer, OfferDetail


class Offer_View(generics.ListCreateAPIView):
    queryset = Offer.objects.all()
    serializer_class = OfferSerializer

    # permission_classes = [IsAdminUser]

    def list(self, request):
        creator_id = request.query_params.get('creator_id', None)
        min_price = request.query_params.get('min_price', None)
        ordering = request.query_params.get('ordering', None)
        max_delivery_time = request.query_params.get('max_delivery_time', None)

        page_size = request.query_params.get('page_size', 6)
        page = request.query_params.get('page', None)

        search = request.query_params.get('search', None)

        if creator_id:
            queryset = self.get_queryset().filter(user=creator_id)
        elif min_price:
            queryset = self.get_queryset().filter(min_price__gte=min_price)
        elif ordering:
            queryset = self.get_queryset().order_by(ordering)
        elif max_delivery_time:
            queryset = self.get_queryset().filter(min_delivery_time__lte=max_delivery_time)
        elif search:
            queryset = self.get_queryset().filter(
                Q(title__icontains=search) | Q(description__icontains=search)
            )
        else:
            queryset = self.get_queryset().filter()

        serializer = OfferSerializer(queryset, many=True)
        return Response(serializer.data)


class SingleOffer_View(generics.RetrieveUpdateDestroyAPIView):
    # permission_classes = [permissions.IsAuthenticated]
    queryset = Offer.objects.all()
    serializer_class = OfferSerializer


class SingleOfferDetails_View(generics.RetrieveAPIView):
    # permission_classes = [permissions.IsAuthenticated]
    queryset = OfferDetail.objects.all()
    serializer_class = OfferDetailSerializer
