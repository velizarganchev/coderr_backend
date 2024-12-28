from rest_framework import generics, permissions, status
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.exceptions import PermissionDenied, NotFound
from rest_framework import filters
from rest_framework.response import Response
from ..models import Review
from .serializers import ReviewSerializer


class ReviewView(generics.ListCreateAPIView):
    """
    ReviewView is a view for listing and creating reviews.
    Attributes:
        permission_classes (list): Specifies that the view requires the user to be authenticated.
        queryset (QuerySet): Defines the base queryset for retrieving reviews.
        serializer_class (Serializer): Specifies the serializer to be used for the reviews.
        filter_backends (list): Specifies the backends to be used for filtering and ordering.
        filterset_fields (list): Defines the fields that can be used for filtering the reviews.
        ordering_fields (list): Defines the fields that can be used for ordering the reviews.
        ordering (list): Specifies the default ordering for the reviews.
    """
    permission_classes = [permissions.IsAuthenticated]

    queryset = Review.objects.all()
    serializer_class = ReviewSerializer

    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['business_user_id', 'reviewer_id']
    ordering_fields = ['updated_at', 'rating']
    ordering = ['-updated_at']


class SingleReviewView(generics.RetrieveUpdateDestroyAPIView):
    """
    SingleReviewView is a view for retrieving, updating, and deleting a single review.
    Attributes:
        permission_classes (list): A list of permission classes that the user must pass to access this view.
        queryset (QuerySet): The queryset that retrieves all Review objects.
        serializer_class (Serializer): The serializer class used for validating and deserializing input, and for serializing output.
    Methods:
        delete(request, pk): Deletes a review if the requesting user is the reviewer.
    """
    permission_classes = [permissions.IsAuthenticated]

    queryset = Review.objects.all()
    serializer_class = ReviewSerializer

    from rest_framework.exceptions import NotFound

    def get_queryset(self):
        """
        Returns the queryset of reviews filtered by the primary key (pk) of the review.
        Raises:
            NotFound: If the review with the specified pk is not found or invalid.
        """
        pk = self.kwargs.get('pk')

        if pk is None:
            raise NotFound(
                detail="Bewertung nicht gefunden. Bitte geben Sie eine ID an.")
        
        try:
            pk = int(pk)
        except ValueError:
            raise NotFound(detail="Die angegebene ID muss eine Ganzzahl sein.")

        queryset = self.queryset.filter(pk=pk)
        if not queryset.exists():
            raise NotFound(
                detail="Bewertung mit der angegebenen ID nicht gefunden.")

        return queryset

    def delete(self, request, pk):
        """
        Deletes a review with the given primary key (pk) if the requesting user is the reviewer.
        Args:
            request (Request): The HTTP request object containing user information.
            pk (int): The primary key of the review to be deleted.
        Returns:
            Response: A response object with a success message and HTTP status 204 if the review is deleted.
                      A response object with an error message and HTTP status 404 if the review is not found.
                      Raises PermissionDenied if the user is not the reviewer of the review.
        """
        try:
            review = Review.objects.get(pk=pk)
            if request.user != review.reviewer:
                raise PermissionDenied(
                    {"detail": "Sie haben keine Berechtigung, diese Bewertung zu löschen."}
                )
        except Review.DoesNotExist:
            return Response(
                {"detail": "Bewertung nicht gefunden."},
                status=status.HTTP_404_NOT_FOUND
            )

        review.delete()
        return Response(
            {"detail": "Bewertung erfolgreich gelöscht."},
            status=status.HTTP_204_NO_CONTENT
        )
