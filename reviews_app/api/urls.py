from django.urls import path
"""
URL configuration for the reviews_app API.
This module defines the URL patterns for the reviews_app API, mapping URL paths to their corresponding views.
Routes:
- 'api/reviews/': Maps to the Review_View class-based view, which handles requests for creating and listing reviews.
- 'api/reviews/<pk>/': Maps to the SingleReview_View class-based view, which handles requests for retrieving, updating, and deleting a single review identified by its primary key (pk).
Imports:
- path: A function from django.urls used to define URL patterns.
- Review_View: A class-based view from the views module that handles review-related requests.
- SingleReview_View: A class-based view from the views module that handles requests for a single review.
"""

from .views import ReviewView, SingleReviewView

urlpatterns = [
    path('api/reviews/', ReviewView.as_view(), name='reviews'),
    path('api/reviews/<pk>/', SingleReviewView.as_view(), name='single_review'),
]
