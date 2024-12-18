from rest_framework import generics, permissions
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from rest_framework.response import Response
from django.db.models import Q

from ..models import Review
from .serializers import ReviewSerializer

class Review_View(generics.ListCreateAPIView):
    """
    API view to list and create reviews.
    """
    permission_classes = [permissions.IsAuthenticated]

    queryset = Review.objects.all()
    serializer_class = ReviewSerializer

    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['business_user_id']
    ordering_fields = ['updated_at']
    ordering = ['-updated_at']

    def get_queryset(self):
        user = self.request.user
        return Review.objects.filter(Q(business_user=user) | Q(reviewer=user))

class SingleReview_View(generics.RetrieveUpdateDestroyAPIView):
    """
    API view to retrieve, update, or delete a single review.
    """
    permission_classes = [permissions.IsAuthenticated]

    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
