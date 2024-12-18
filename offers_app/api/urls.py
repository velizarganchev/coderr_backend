from django.urls import path

from offers_app.api.views import Offer_View, SingleOffer_View, SingleOfferDetails_View

urlpatterns = [
    # URL pattern for the list of offers
    path('api/offers/', Offer_View.as_view(), name='offers'),
    # URL pattern for a single offer
    path('api/offers/<pk>/', SingleOffer_View.as_view(), name='single_offer'),
    # URL pattern for the details of a single offer
    path('api/offerdetails/<pk>/', SingleOfferDetails_View.as_view(), name='single_offer_details')
]
