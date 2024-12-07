from django.urls import path

from .views import Review_View, SingleReview_View

urlpatterns = [
    path('api/reviews/', Review_View.as_view(), name='reviews'),
    path('api/reviews/<pk>/', SingleReview_View.as_view(), name='single_review'),
]
