from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token


class UserTests(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            username='testuser', password='testpassword')
        cls.token = Token.objects.create(user=cls.user)
        cls.register_url = reverse('registration')
        cls.login_url = reverse('login')
        cls.profile_url = reverse(
            'profile_detail', kwargs={'uid': cls.user.id})

    def test_register_user_successful(self):
        data = {
            "username": "newuser",
            "password": "newpassword",
            "email": "newuser@example.com",
            "repeated_password": "newpassword",
            "type": "customer"
        }
        response = self.client.post(self.register_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 2)

    def test_register_user_passwords_do_not_match(self):
        data = {
            "username": "newuser",
            "password": "password1",
            "repeated_password": "password2",
            "email": "newuser@example.com"
        }
        response = self.client.post(self.register_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_user_invalid_data(self):
        data = {"username": ""}
        response = self.client.post(self.register_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_user_successful(self):
        data = {
            "username": "testuser",
            "password": "testpassword"
        }
        response = self.client.post(self.login_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_login_user_invalid_credentials(self):
        data = {
            "username": "testuser",
            "password": "wrongpassword"
        }
        response = self.client.post(self.login_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_profile_successful(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        response = self.client.get(self.profile_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_profile_unauthorized(self):
        response = self.client.get(self.profile_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_profile_successful(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        data = {"email": "updatedemail@example.com"}
        response = self.client.patch(self.profile_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertEqual(self.user.email, "updatedemail@example.com")

    def test_update_profile_invalid_data(self):
        self.client.credentials(
            HTTP_AUTHORIZATION='Token ' + self.token.key)
        data = {"email": "updatedemail@example.com"}
        response = self.client.put(self.profile_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_profile_unauthorized(self):
        data = {"email": "updatedemail@example.com"}
        response = self.client.patch(self.profile_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_profile_invalid_token(self):
        self.client.credentials(
            HTTP_AUTHORIZATION='Token ' + self.token.key + 'invalid')
        data = {"email": "updatedemail@example.com"}
        response = self.client.patch(self.profile_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_customer_profile_type_successful(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        response = self.client.get(
            reverse('profiletype', kwargs={'type': 'customer'}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_business_profile_type_successful(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        response = self.client.get(
            reverse('profiletype', kwargs={'type': 'business'}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_profile_type_invalid_type(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        response = self.client.get(
            reverse('profiletype', kwargs={'type': 'invalid'}))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_delete_profile_successful(self):
        self.user.is_staff = True
        self.user.save()
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        response = self.client.delete(self.profile_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(User.objects.count(), 0)

    def test_logout_user_successful(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        response = self.client.post(reverse('logout'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Token.objects.count(), 0)
