from rest_framework import generics, permissions, status
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.exceptions import PermissionDenied
from rest_framework import filters
from rest_framework.response import Response
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
    filterset_fields = ['business_user_id', 'reviewer_id']
    ordering_fields = ['updated_at', 'rating']
    ordering = ['-updated_at']


class SingleReview_View(generics.RetrieveUpdateDestroyAPIView):
    """
    API view to retrieve, update, or delete a single review.
    """
    permission_classes = [permissions.IsAuthenticated]

    queryset = Review.objects.all()
    serializer_class = ReviewSerializer

    def delete(self, request, pk):
        """
        Handle deletion of an review.
        """
        try:
            review = Review.objects.get(pk=pk)
        except Review.DoesNotExist:
            return Response(
                {"error": "Bewertung nicht gefunden."},
                status=status.HTTP_404_NOT_FOUND
            )

        if not request.user == review.reviewer:
            raise PermissionDenied(
                {"error": "Sie haben keine Berechtigung, diese Bewertung zu löschen."}
            )

        Review.delete()
        return Response(
            {"message": "Bewertung erfolgreich gelöscht."},
            status=status.HTTP_204_NO_CONTENT
        )
