from rest_framework import generics, permissions, status
from rest_framework.exceptions import PermissionDenied, NotFound, ValidationError
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters

from django.db.models import Q

from .serializers import OfferSerializer, SingleOfferSerializer, OfferDetailSerializer
from ..models import Offer, OfferDetail


class OfferPagination(PageNumberPagination):
    """Custom Pagination for Offers."""
    page_size = 6
    page_size_query_param = 'page_size'
    max_page_size = 50


class OfferView(generics.ListCreateAPIView):
    """
    API view to list and create offers.

    Query Parameters:
    - creator_id: Filter by the creator's user ID
    - search: Search in offer title or description
    - max_delivery_time: Filter offers with delivery time <= max_delivery_time
    """
    permission_classes = [permissions.IsAuthenticated]

    queryset = Offer.objects.all()
    serializer_class = OfferSerializer
    pagination_class = OfferPagination
    filter_backends = [DjangoFilterBackend,
                       filters.OrderingFilter, filters.SearchFilter]

    search_fields = ['title', 'description']
    ordering_fields = ['min_price', 'updated_at']
    ordering = ['min_price']

    def get_queryset(self):
        queryset = super().get_queryset()

        creator_id = self.request.query_params.get('creator_id')
        max_delivery_time = self.request.query_params.get('max_delivery_time')

        if creator_id:
            try:
                creator_id = int(creator_id)
                queryset = queryset.filter(user_id=creator_id)
            except ValueError:
                raise ValidationError(
                    {'creator_id': 'Muss eine ganze Zahl sein.'})

        if max_delivery_time:
            try:
                max_delivery_time = int(max_delivery_time)
                queryset = queryset.filter(
                    min_delivery_time__lte=max_delivery_time)
            except ValueError:
                raise ValidationError(
                    {'max_delivery_time': 'Muss eine ganze Zahl sein.'})

        return queryset


class SingleOfferView(generics.RetrieveUpdateDestroyAPIView):
    """
    API view to retrieve, update and delete a single offer.
    """
    permission_classes = [permissions.IsAuthenticated]
    queryset = Offer.objects.all()
    serializer_class = SingleOfferSerializer

    def perform_destroy(self, instance):
        """
        Custom deletion logic.
        """
        if not self.request.user == instance.user:
            raise PermissionDenied(
                {"detail": "Sie haben keine Berechtigung, dieses Angebot zu löschen."}
            )
        instance.delete()

    def delete(self, request, *args, **kwargs):
        """
        Override delete to provide a custom error message if the object doesn't exist.
        """
        try:
            return super().delete(request, *args, **kwargs)
        except NotFound:
            return Response(
                {"detail": "Angebot nicht gefunden."},
                status=status.HTTP_404_NOT_FOUND
            )


class SingleOfferDetailsView(generics.RetrieveUpdateAPIView):
    """
    API view to retrieve details of a single offer.
    """
    permission_classes = [permissions.IsAuthenticated]
    queryset = OfferDetail.objects.all()
    serializer_class = OfferDetailSerializer
