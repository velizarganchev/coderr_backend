from rest_framework import generics

from ..models import Review
from .serializers import ReviewSerializer


class Review_View(generics.ListCreateAPIView):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer


class SingleReview_View(generics.RetrieveUpdateDestroyAPIView):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
