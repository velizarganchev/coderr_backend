from rest_framework import generics, permissions
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from rest_framework.response import Response

from ..models import Review
from .serializers import ReviewSerializer


class Review_View(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated]

    queryset = Review.objects.all()
    serializer_class = ReviewSerializer

    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['business_user_id']
    ordering_fields = ['updated_at']
    ordering = ['-updated_at']


class SingleReview_View(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [permissions.IsAuthenticated]

    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
