from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from ..models import Review


class ReviewTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser', password='testpass')
        self.token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        self.business_user = User.objects.create_user(
            username='businessuser', password='businesspass')

    def test_create_review(self):
        url = reverse('reviews')
        data = {
            'business_user': self.business_user.id,
            'rating': 5,
            'description': 'Great service!'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Review.objects.count(), 1)
        self.assertEqual(Review.objects.get().rating, 5)

    def test_create_review_without_token(self):
        self.client.credentials()  # Remove token
        url = reverse('reviews')
        data = {
            'business_user': self.business_user.id,
            'rating': 5,
            'description': 'Great service!'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_duplicate_review(self):
        Review.objects.create(business_user=self.business_user,
                              reviewer=self.user, rating=4, description='Good service')
        url = reverse('reviews')
        data = {
            'business_user': self.business_user.id,
            'rating': 5,
            'description': 'Great service!'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_reviews(self):
        Review.objects.create(business_user=self.business_user,
                              reviewer=self.user, rating=4, description='Good service')
        url = reverse('reviews')
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_get_single_review(self):
        review = Review.objects.create(
            business_user=self.business_user, reviewer=self.user, rating=4, description='Good service')
        url = reverse('single_review', kwargs={'pk': review.pk})
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['rating'], 4)

    def test_update_review(self):
        review = Review.objects.create(
            business_user=self.business_user, reviewer=self.user, rating=4, description='Good service')
        url = reverse('single_review', kwargs={'pk': review.pk})
        data = {
            'rating': 5,
            'description': 'Excellent service!'
        }
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        review.refresh_from_db()
        self.assertEqual(review.rating, 5)
        self.assertEqual(review.description, 'Excellent service!')

    def test_delete_review(self):
        review = Review.objects.create(
            business_user=self.business_user, reviewer=self.user, rating=4, description='Good service')
        url = reverse('single_review', kwargs={'pk': review.pk})
        response = self.client.delete(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Review.objects.count(), 0)
