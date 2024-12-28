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
            username='testuser', email="test@hotmail.com", password='testpassword')
        cls.user.userprofile.type = "business"
        cls.user.save()
        cls.token = Token.objects.create(user=cls.user)

        cls.offer_url = reverse('offers')
        cls.single_offer_url = lambda pk: reverse(
            'single_offer', kwargs={'pk': pk})

    def setUp(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')

    def create_feature(self, name="Default Feature"):
        return Feature.objects.create(name=name)

    def create_offer(self, title="Default Title", description="Default Description"):
        return Offer.objects.create(user=self.user, title=title, description=description)

    def test_create_offer_successful(self):
        feature1 = self.create_feature("Logo Design")
        feature2 = self.create_feature("Visitenkarte")
        feature3 = self.create_feature("Briefpapier")
        feature4 = self.create_feature("Flyer")

        data = {
            "title": "Test Offer",
            "image": None,
            "description": "Description",
            "details": [
                {
                    "title": "Basic Design",
                    "revisions": 2,
                    "delivery_time_in_days": 5,
                    "price": 100.00,
                    "features": [feature1.name, feature2.name],
                    "offer_type": "basic"
                },
                {
                    "title": "Standard Design",
                    "revisions": 5,
                    "delivery_time_in_days": 7,
                    "price": 200.00,
                    "features": [feature1.name, feature2.name, feature3.name],
                    "offer_type": "standard"
                },
                {
                    "title": "Premium Design",
                    "revisions": 10,
                    "delivery_time_in_days": 10,
                    "price": 500.00,
                    "features": [feature1.name, feature2.name, feature3.name, feature4.name],
                    "offer_type": "premium"
                }
            ]
        }

        response = self.client.post(self.offer_url, data, format='json')

        self.assertEqual(response.status_code,
                         status.HTTP_201_CREATED, "Offer creation failed")
        self.assertEqual(Offer.objects.count(), 1,
                         "Offer not created in the database")
        self.assertEqual(OfferDetail.objects.count(),
                         3, "OfferDetail not created")
        self.assertEqual(Feature.objects.count(), 4,
                         "Features not created correctly")

    def test_create_offer_with_invalid_user(self):
        self.user.userprofile.type = "customer"
        self.user.save()

        data = {
            "title": "Test Offer",
            "description": "Description",
            "details": []
        }
        response = self.client.post(self.offer_url, data, format='json')

        self.assertEqual(response.status_code,
                         status.HTTP_401_UNAUTHORIZED, "Invalid user accepted")

    def test_create_offer_with_missing_details(self):
        data = {
            "title": "Test Offer Without Details",
            "description": "Missing details",
        }
        response = self.client.post(self.offer_url, data, format='json')

        self.assertEqual(response.status_code,
                         status.HTTP_400_BAD_REQUEST, "Invalid data accepted")
        self.assertIn('details', response.data,
                      "Error message for missing details not found")

    def test_get_all_offers_successful(self):
        self.create_offer()
        response = self.client.get(self.offer_url)
        self.assertEqual(response.status_code,
                         status.HTTP_200_OK, "Offers not found")

    def test_get_all_offers_with_creator_id_query_params(self):
        self.create_offer()
        response = self.client.get(
            self.offer_url, {'creator_id': self.user.id})
        self.assertEqual(response.status_code,
                         status.HTTP_200_OK, "Offers not found")

    def test_get_all_offers_with_invalid_creator_id_query_params(self):
        self.create_offer()
        response = self.client.get(self.offer_url, {'creator_id': 'invalid'})
        self.assertEqual(response.status_code,
                         status.HTTP_400_BAD_REQUEST, "Invalid creator_id accepted")

    def test_get_all_offers_with_max_delivery_time_query_params(self):
        self.create_offer()
        response = self.client.get(self.offer_url, {'max_delivery_time': 5})
        self.assertEqual(response.status_code,
                         status.HTTP_200_OK, "Offers not found")

    def test_get_all_offers_with_invalid_max_delivery_time_query_params(self):
        self.create_offer()
        response = self.client.get(
            self.offer_url, {'max_delivery_time': 'invalid'})
        self.assertEqual(response.status_code,
                         status.HTTP_400_BAD_REQUEST, "Invalid max_delivery_time accepted")

    def test_get_all_offers_with_search_query_params(self):
        self.create_offer()
        response = self.client.get(self.offer_url, {'search': 'Default'})
        self.assertEqual(response.status_code,
                         status.HTTP_200_OK, "Offers not found")

    def test_get_all_offers_with_invalid_search_query_params(self):
        self.create_offer()
        response = self.client.get(self.offer_url, {'search': 'Invalid'})
        self.assertEqual(response.status_code,
                         status.HTTP_200_OK, "Invalid search accepted")

    def test_get_single_offer_successful(self):
        offer = self.create_offer()
        response = self.client.get(self.single_offer_url(offer.id))
        self.assertEqual(response.status_code,
                         status.HTTP_200_OK, "Offer not found")

    def test_get_single_offer_invalid_id(self):
        response = self.client.get(self.single_offer_url(0))
        self.assertEqual(response.status_code,
                         status.HTTP_404_NOT_FOUND, "Invalid offer id found")

    def test_update_offer_successful(self):
        offer = self.create_offer()
        data = {
            "title": "Updated Title",
            "description": "Updated Description"
        }

        response = self.client.patch(
            self.single_offer_url(offer.id), data, format='json')
        self.assertEqual(response.status_code,
                         status.HTTP_200_OK, "Offer update failed")

        offer.refresh_from_db()
        self.assertEqual(offer.title, data['title'], "Title not updated")
        self.assertEqual(offer.description, data['description'],
                         "Description not updated")

    def test_update_offer_with_invalid_data(self):
        offer = self.create_offer()
        data = {
            "title": "Updated Title",
            "description": "Updated Description",
            "invalid_key": "Invalid Value"
        }

        response = self.client.put(
            self.single_offer_url(offer.id), data, format='json')
        self.assertEqual(response.status_code,
                         status.HTTP_400_BAD_REQUEST, "Invalid data accepted")

    def test_update_offer_with_invalid_token(self):
        self.client.credentials()
        offer = self.create_offer()
        data = {
            "title": "Updated Title",
            "description": "Updated Description"
        }
        response = self.client.patch(
            self.single_offer_url(offer.id), data, format='json')
        self.assertEqual(response.status_code,
                         status.HTTP_401_UNAUTHORIZED, "Invalid token accepted")

    def test_get_offer_details_successful(self):
        offer = self.create_offer()
        OfferDetail.objects.create(
            offer=offer,
            title="Basic Package",
            revisions=2,
            delivery_time_in_days=5,
            price=100,
            offer_type="basic"
        )

        response = self.client.get(self.single_offer_url(offer.id))
        self.assertEqual(response.status_code,
                         status.HTTP_200_OK, "Offer details not found")

    def test_get_offer_details_invalid_id(self):
        response = self.client.get(self.single_offer_url(0))
        self.assertEqual(response.status_code,
                         status.HTTP_404_NOT_FOUND, "Invalid offer id found")

    def test_get_offers_with_search_query_params(self):
        offer = self.create_offer()
        OfferDetail.objects.create(
            offer=offer,
            title="Basic Package",
            revisions=2,
            delivery_time_in_days=5,
            price=100,
            offer_type="basic"
        )

        response = self.client.get(self.offer_url, {'search': 'Basic'})
        self.assertEqual(response.status_code,
                         status.HTTP_200_OK, "Offer details not found")

    def test_get_offers_with_creator_id_query_params(self):
        offer = self.create_offer()
        OfferDetail.objects.create(
            offer=offer,
            title="Basic Package",
            revisions=2,
            delivery_time_in_days=5,
            price=100,
            offer_type="basic"
        )

        response = self.client.get(
            self.offer_url, {'creator_id': offer.user.id})
        self.assertEqual(response.status_code,
                         status.HTTP_200_OK, "Offer details not found")

    def test_delete_offer_with_related_details(self):
        offer = self.create_offer()
        OfferDetail.objects.create(
            offer=offer,
            title="Basic Package",
            revisions=2,
            delivery_time_in_days=5,
            price=100,
            offer_type="basic"
        )

        response = self.client.delete(self.single_offer_url(offer.id))
        self.assertEqual(response.status_code,
                         status.HTTP_204_NO_CONTENT, "Offer deletion failed")

        self.assertEqual(Offer.objects.count(), 0, "Offer not deleted")
        self.assertEqual(OfferDetail.objects.count(),
                         0, "OfferDetail not deleted")
