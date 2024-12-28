from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from offers_app.models import Offer, OfferDetail, Feature
from ..models import Order


class OrderTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser', password='testpassword')
        self.user.userprofile.type = 'customer'
        self.user.userprofile.save()
        self.token = Token.objects.create(user=self.user)

        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        self.order_url = reverse('orders')
        self.single_order_url = lambda pk: reverse(
            'single_order', kwargs={'pk': pk})
        self.not_completed_order_count_url = lambda pk: reverse(
            'not_completed_order', kwargs={'pk': pk})
        self.completed_order_count_url = lambda pk: reverse(
            'completed_order', kwargs={'pk': pk})

        self.business_user = User.objects.create_user(
            username='businessuser', password='businesspassword')
        self.business_user.userprofile.type = 'business'
        self.business_user.userprofile.save()

        self.business_token = Token.objects.create(user=self.business_user)

        self.offer = Offer.objects.create(
            user=self.business_user, title="Test Offer", description="This is a test offer")
        self.feature = Feature.objects.create(name="Feature 1")
        self.offer_detail = OfferDetail.objects.create(
            offer=self.offer, title="Basic Package", revisions=2, delivery_time_in_days=5, price=100, offer_type="basic")
        self.offer_detail.features.add(self.feature)

    def test_create_order(self):
        data = {
            "offer_detail_id": self.offer_detail.id
        }
        response = self.client.post(self.order_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Order.objects.count(), 1)

    def test_create_order_with_invalid_user(self):
        data = {
            "offer_detail_id": self.offer_detail.id
        }
        self.client.credentials(
            HTTP_AUTHORIZATION='Token ' + self.business_token.key)
        response = self.client.post(self.order_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_order_with_invalid_offer_detail_id(self):
        data = {
            "offer_detail_id": 100
        }
        response = self.client.post(self.order_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_orders(self):
        Order.objects.create(
            customer_user=self.user, business_user=self.business_user, title="Basic Package",
            revisions=2, delivery_time_in_days=5, price=100, offer_type="basic")
        response = self.client.get(self.order_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_get_orders_with_invalid_token(self):
        Order.objects.create(
            customer_user=self.user, business_user=self.business_user, title="Basic Package",
            revisions=2, delivery_time_in_days=5, price=100, offer_type="basic")
        self.client.credentials(
            HTTP_AUTHORIZATION='Token ' + self.token.key + 'invalid')
        response = self.client.get(self.order_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_single_order(self):
        order = Order.objects.create(
            customer_user=self.user, business_user=self.business_user, title="Basic Package",
            revisions=2, delivery_time_in_days=5, price=100, offer_type="basic")
        response = self.client.get(self.single_order_url(order.id))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], "Basic Package")

    def test_get_single_order_invalid_id(self):
        response = self.client.get(self.single_order_url(0))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_order_status(self):
        order = Order.objects.create(
            customer_user=self.user, business_user=self.business_user, title="Basic Package",
            revisions=2, delivery_time_in_days=5, price=100, offer_type="basic")
        data = {"status": "completed"}

        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        response = self.client.patch(
            self.single_order_url(order.id), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        business_token = self.business_token.key
        self.client.credentials(
            HTTP_AUTHORIZATION='Token ' + business_token)
        response = self.client.patch(
            self.single_order_url(order.id), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        order.refresh_from_db()
        self.assertEqual(order.status, "completed")

    def test_delete_order(self):
        self.user.is_staff = True
        self.user.save()
        order = Order.objects.create(
            customer_user=self.user, business_user=self.business_user, title="Basic Package",
            revisions=2, delivery_time_in_days=5, price=100, offer_type="basic")
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        response = self.client.delete(self.single_order_url(order.id))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Order.objects.count(), 0)

    def test_get_not_completed_order_count(self):
        Order.objects.create(
            customer_user=self.user, business_user=self.business_user, title="Basic Package",
            revisions=2, delivery_time_in_days=5, price=100, offer_type="basic", status="in_progress")
        response = self.client.get(
            self.not_completed_order_count_url(self.user.id))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['order_count'], 1)

    def test_not_completed_order_count_with_invalid_user_id(self):
        response = self.client.get(
            self.not_completed_order_count_url(100))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_completed_order_count(self):
        Order.objects.create(
            customer_user=self.user, business_user=self.business_user, title="Basic Package",
            revisions=2, delivery_time_in_days=5, price=100, offer_type="basic", status="completed")
        response = self.client.get(
            self.completed_order_count_url(self.user.id))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['completed_order_count'], 1)

    def test_completed_order_count_with_invalid_user(self):
        response = self.client.get(
            self.completed_order_count_url(100))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
