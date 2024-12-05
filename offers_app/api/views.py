from rest_framework import generics

from .serializers import OfferSerializer, OfferDetailSerializer
from ..models import Offer, OfferDetail


class Offer_View(generics.ListCreateAPIView):
    queryset = Offer.objects.all()
    serializer_class = OfferSerializer
    # permission_classes = [IsAdminUser]

    # def list(self, request):
    #     # Note the use of `get_queryset()` instead of `self.queryset`
    #     queryset = self.get_queryset()
    #     serializer = UserSerializer(queryset, many=True)
    #     return Response(serializer.data)


class SingleOffer_View(generics.RetrieveUpdateDestroyAPIView):
    # permission_classes = [permissions.IsAuthenticated]
    queryset = Offer.objects.all()
    serializer_class = OfferSerializer


class SingleOfferDetails_View(generics.RetrieveAPIView):
    # permission_classes = [permissions.IsAuthenticated]
    queryset = OfferDetail.objects.all()
    serializer_class = OfferDetailSerializer
