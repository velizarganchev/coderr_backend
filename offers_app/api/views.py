from rest_framework import generics, permissions, status
from rest_framework.exceptions import PermissionDenied, NotFound
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


class Offer_View(generics.ListCreateAPIView):
    """
    API view to list and create offers.
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
        search = self.request.query_params.get('search')
        max_delivery_time = self.request.query_params.get('max_delivery_time')

        if not creator_id and not search and not max_delivery_time:
            return queryset.none()

        if creator_id:
            queryset = queryset.filter(user_id=creator_id)

        if max_delivery_time:
            queryset = queryset.filter(
                min_delivery_time__lte=max_delivery_time)

        return queryset

    def list(self, request, *args, **kwargs):
        """Override the list method to add custom response structure."""
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'count': len(serializer.data),
            'results': serializer.data
        })


class SingleOffer_View(generics.RetrieveUpdateDestroyAPIView):
    """
    API view to retrieve, update, or delete a single offer.
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


class SingleOfferDetails_View(generics.RetrieveUpdateDestroyAPIView):
    """
    API view to retrieve details of a single offer.
    """
    permission_classes = [permissions.IsAuthenticated]
    queryset = OfferDetail.objects.all()
    serializer_class = OfferDetailSerializer
