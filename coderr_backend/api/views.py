from django.db.models import Avg

from rest_framework.views import APIView
from rest_framework.response import Response
from offers_app.models import Offer
from reviews_app.models import Review
from user_auth_app.models import UserProfile


class BaseInfo_View(APIView):
    def get(self, request):
        """
        Handle GET request and return base information including offer count, review count,
        average rating, and business profile count.

        average_rating = reviews.aggregate(Avg('rating'))['rating__avg']
            request (Request): The request object.

        Returns:
            Response: A response object containing the base information.
        """
        reviews = Review.objects.all()

        offer_count = Offer.objects.all().count()
        review_count = reviews.count()
        average_rating = reviews.aggregate(Avg('rating'))['rating__avg']
        business_profile_count = UserProfile.objects.filter(type='business').count()

        return Response({
            "offer_count": offer_count,
            "review_count": review_count,
            "average_rating": average_rating,
            "business_profile_count": business_profile_count
        })
