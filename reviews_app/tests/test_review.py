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
        self.user.userprofile.type = 'customer'
        self.token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        self.business_user = User.objects.create_user(
            username='businessuser', password='businesspass')
        self.reviews_url = reverse('reviews')
        self.single_review_url = lambda pk: reverse(
            'single_review', kwargs={'pk': pk})

    def test_create_review(self):
        url = self.reviews_url
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
        self.client.credentials()
        url = self.reviews_url
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
        url = self.reviews_url
        data = {
            'business_user': self.business_user.id,
            'rating': 5,
            'description': 'Great service!'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_review_with_business_user(self):
        self.user.userprofile.type = 'business'
        self.user.save()
        url = self.reviews_url
        data = {
            'business_user': self.business_user.id,
            'rating': 5,
            'description': 'Great service!'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_review_with_invalid_rating(self):
        url = self.reviews_url
        data = {
            'business_user': self.business_user.id,
            'rating': 6,
            'description': 'Great service!'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_reviews(self):
        Review.objects.create(business_user=self.business_user,
                              reviewer=self.user, rating=4, description='Good service')
        url = self.reviews_url
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_get_single_review(self):
        review = Review.objects.create(
            business_user=self.business_user, reviewer=self.user, rating=4, description='Good service')
        url = self.single_review_url(review.pk)
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['rating'], 4)

    def test_get_single_review_without_token(self):
        review = Review.objects.create(
            business_user=self.business_user, reviewer=self.user, rating=4, description='Good service')
        url = self.single_review_url(review.pk)
        self.client.credentials()
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_non_existent_review(self):
        url = self.single_review_url(1)
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_review(self):
        review = Review.objects.create(
            business_user=self.business_user, reviewer=self.user, rating=4, description='Good service')
        url = self.single_review_url(review.pk)
        data = {
            'rating': 5,
            'description': 'Excellent service!'
        }
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        review.refresh_from_db()
        self.assertEqual(review.rating, 5)
        self.assertEqual(review.description, 'Excellent service!')

    def test_update_review_with_invalid_token(self):
        review = Review.objects.create(
            business_user=self.business_user, reviewer=self.user, rating=4, description='Good service')
        url = self.single_review_url(review.pk)
        data = {
            'rating': 5,
            'description': 'Excellent service!'
        }
        self.client.credentials(
            HTTP_AUTHORIZATION='Token ' + self.token.key + 'invalid')
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_review_without_token(self):
        review = Review.objects.create(
            business_user=self.business_user, reviewer=self.user, rating=4, description='Good service')
        url = self.single_review_url(review.pk)
        data = {
            'rating': 5,
            'description': 'Excellent service!'
        }
        self.client.credentials()
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_delete_review(self):
        review = Review.objects.create(
            business_user=self.business_user, reviewer=self.user, rating=4, description='Good service')
        url = self.single_review_url(review.pk)
        response = self.client.delete(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Review.objects.count(), 0)

    def test_delete_review_without_token(self):
        review = Review.objects.create(
            business_user=self.business_user, reviewer=self.user, rating=4, description='Good service')
        url = self.single_review_url(review.pk)
        self.client.credentials()
        response = self.client.delete(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_delete_review_with_invalid_token(self):
        review = Review.objects.create(
            business_user=self.business_user, reviewer=self.user, rating=4, description='Good service')
        url = self.single_review_url(review.pk)
        self.client.credentials(
            HTTP_AUTHORIZATION='Token ' + self.token.key + 'invalid')
        response = self.client.delete(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
