from django.urls import path

from offers_app.api.views import OfferView, SingleOfferView, SingleOfferDetailsView

urlpatterns = [
    # URL pattern for the list of offers
    path('api/offers/', OfferView.as_view(), name='offers'),
    # URL pattern for a single offer
    path('api/offers/<pk>/', SingleOfferView.as_view(), name='single_offer'),
    # URL pattern for the details of a single offer
    path('api/offerdetails/<pk>/', SingleOfferDetailsView.as_view(),
         name='single_offer_details')
]
