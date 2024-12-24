from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from ..models import Offer, OfferDetail, Feature


class OfferTests(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            username='testuser', password='testpassword')
        cls.token = Token.objects.create(user=cls.user)
        cls.user.userprofile.type = 'business'
        cls.user.userprofile.save()

        cls.offer_url = reverse('offers')
        cls.single_offer_url = lambda pk: reverse(
            'single_offer', kwargs={'pk': pk})
        cls.single_offer_details_url = lambda pk: reverse(
            'single_offer_details', kwargs={'pk': pk})

    def setUp(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)

    def create_feature(self, name="Feature"):
        return Feature.objects.create(name=name)

    def create_offer(self, title="Test Offer", description="Description"):
        return Offer.objects.create(user=self.user, title=title, description=description)

    def test_create_offer_successful(self):
        feature1 = self.create_feature(name="Feature 1")
        feature2 = self.create_feature(name="Feature 2")

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
        self.assertEqual(response.status_code,
                         status.HTTP_201_CREATED, "Offer creation failed")
        self.assertEqual(Offer.objects.count(), 1)
        self.assertEqual(OfferDetail.objects.count(), 1)
        self.assertEqual(Feature.objects.count(), 2)

    def test_create_offer_invalid_data(self):
        data = {"title": ""}
        response = self.client.post(self.offer_url, data, format='json')
        self.assertEqual(response.status_code,
                         status.HTTP_400_BAD_REQUEST, "Invalid data accepted")
        self.assertIn('title', response.data)

    def test_get_offers_successful(self):
        self.create_offer()
        response = self.client.get(self.offer_url, {'creator_id': 1})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

    def test_get_single_offer_valid(self):
        offer = self.create_offer()
        response = self.client.get(self.single_offer_url(offer.id))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], "Test Offer")

    def test_get_single_offer_not_found(self):
        response = self.client.get(self.single_offer_url(999))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_offer_successful(self):
        offer = self.create_offer()
        data = {"title": "Updated Offer"}
        response = self.client.patch(
            self.single_offer_url(offer.id), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        offer.refresh_from_db()
        self.assertEqual(offer.title, "Updated Offer")

    def test_delete_offer_successful(self):
        offer = self.create_offer()
        response = self.client.delete(self.single_offer_url(offer.id))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Offer.objects.count(), 0)

    def test_delete_offer_with_details(self):
        offer = self.create_offer()
        OfferDetail.objects.create(
            offer=offer, title="Basic Package", revisions=2, delivery_time_in_days=5, price=100, offer_type="basic")
        response = self.client.delete(self.single_offer_url(offer.id))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Offer.objects.count(), 0)
        self.assertEqual(OfferDetail.objects.count(), 0)

    def test_access_denied_without_token(self):
        self.client.credentials()
        response = self.client.get(self.offer_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
