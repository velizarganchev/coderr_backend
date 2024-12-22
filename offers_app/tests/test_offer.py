from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from ..models import Offer, OfferDetail, Feature


class OfferTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser', password='testpassword')
        self.token = Token.objects.create(user=self.user)
        self.user.userprofile.type = 'business'
        self.user.userprofile.save()

        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        self.offer_url = reverse('offers')
        self.single_offer_url = lambda pk: reverse(
            'single_offer', kwargs={'pk': pk})
        self.single_offer_details_url = lambda pk: reverse(
            'single_offer_details', kwargs={'pk': pk})

    def test_create_offer(self):
        feature1 = Feature.objects.create(name="Feature 1")
        feature2 = Feature.objects.create(name="Feature 2")

        data = {
            "title": "Test Offer",
            "description": "This is a test offer",
            "details": [
                {
                    "title": "Basic Package",
                    "revisions": 2,
                    "delivery_time_in_days": 5,
                    "price": 100,
                    "features": [feature1.name, feature2.name],
                    "offer_type": "basic"
                }
            ]
        }
        response = self.client.post(self.offer_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Offer.objects.count(), 1)
        self.assertEqual(OfferDetail.objects.count(), 1)
        self.assertEqual(Feature.objects.count(), 2)

    def test_get_offers(self):
        Offer.objects.create(user=self.user, title="Test Offer",
                             description="This is a test offer")
        response = self.client.get(self.offer_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

    def test_get_single_offer(self):
        offer = Offer.objects.create(
            user=self.user, title="Test Offer", description="This is a test offer")
        response = self.client.get(self.single_offer_url(offer.id))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], "Test Offer")

    def test_update_offer(self):
        offer = Offer.objects.create(
            user=self.user, title="Test Offer", description="This is a test offer")
        data = {"title": "Updated Offer"}
        response = self.client.patch(
            self.single_offer_url(offer.id), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        offer.refresh_from_db()
        self.assertEqual(offer.title, "Updated Offer")

    def test_delete_offer(self):
        offer = Offer.objects.create(
            user=self.user, title="Test Offer", description="This is a test offer")
        response = self.client.delete(self.single_offer_url(offer.id))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Offer.objects.count(), 0)

    def test_get_offer_details(self):
        offer = Offer.objects.create(
            user=self.user, title="Test Offer", description="This is a test offer")
        offer_detail = OfferDetail.objects.create(
            offer=offer, title="Basic Package", revisions=2, delivery_time_in_days=5, price=100, offer_type="basic")
        response = self.client.get(
            self.single_offer_details_url(offer_detail.id))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], "Basic Package")
