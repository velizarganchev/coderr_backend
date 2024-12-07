from django.urls import path

from offers_app.api.views import Offer_View, SingleOffer_View, SingleOfferDetails_View

urlpatterns = [
    path('api/offers/', Offer_View.as_view(), name='offers'),
    path('api/offers/<pk>/', SingleOffer_View.as_view(), name='single_offer'),
    path('api/offerdetails/<pk>/', SingleOfferDetails_View.as_view(),
         name='single_offer_details')
]
