from django.urls import path

from offers_app.api.views import Offer_View, SingleOffer_View, SingleOfferDetails_View

urlpatterns = [
    path('offers/', Offer_View.as_view(), name='offers'),
    path('offers/<pk>/', SingleOffer_View.as_view(), name='single_offer'),
    path('offerdetails/<pk>/', SingleOfferDetails_View.as_view(),
         name='single_offer_details'),
    path('orders/', Offer_View.as_view(), name='offers'),
    path('orders/<pk>/', SingleOffer_View.as_view(), name='single_offer'),
]
