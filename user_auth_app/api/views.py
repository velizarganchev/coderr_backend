from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated, AllowAny

from django.contrib.auth.models import User
from django.contrib.auth import authenticate

from user_auth_app.api.serializers import UserProfileSerializer, UserProfileTypeSerializer
from user_auth_app.models import UserProfile


class UserProfileType_View(APIView):
    """
    API view to retrieve user profiles by type.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, type=None, format=None):
        """
        Handles GET requests to retrieve user profiles based on the specified type.

        Args:
            request (Request): The HTTP request object.
            type (str, optional): The type of user profiles to filter by. Defaults to None.
            format (str, optional): The format of the response. Defaults to None.

        Returns:
            Response: A Response object containing serialized user profiles if type is provided,
                      or an error message if type is not provided.
        """
        if type:
            if type not in ['customer', 'business']:
                return Response({'detail': 'Ungültiger Typ.'}, status=status.HTTP_400_BAD_REQUEST)

            userprofiles = UserProfile.objects.filter(type=type)
            serializer = UserProfileTypeSerializer(userprofiles, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response({'detail': 'Typ ist erforderlich.'}, status=status.HTTP_400_BAD_REQUEST)


class UserProfile_View(APIView):
    """
    API view to retrieve, update, or delete user profiles.
    """
    permission_classes = [IsAuthenticated]

    def get_user_profile(self, uid):
        """
        Retrieve the user profile for a given user ID.

        Args:
            uid (int): The unique identifier of the user.

        Returns:
            UserProfile: The user profile associated with the given user ID, or None if the user or user profile does not exist.
        """
        try:
            user = User.objects.get(pk=uid)
            return UserProfile.objects.get(user=user)
        except (User.DoesNotExist, UserProfile.DoesNotExist):
            return None

    def get(self, request, uid=None, format=None):
        """
        Retrieve user profile(s).
        If a user ID (uid) is provided, retrieve the specific user profile.
        If no user ID is provided, retrieve all user profiles.
        Args:
            request (Request): The HTTP request object.
            uid (str, optional): The user ID. Defaults to None.
            format (str, optional): The format of the response. Defaults to None.
        Returns:
            Response: A Response object containing the serialized user profile data
                      and the appropriate HTTP status code.
        """

        if uid:
            userprofile = self.get_user_profile(uid)
            if not userprofile:
                return Response({'detail': 'User Profile not found'},
                                status=status.HTTP_404_NOT_FOUND)
            serializer = UserProfileSerializer(userprofile)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            userprofiles = UserProfile.objects.all()
            serializer = UserProfileSerializer(userprofiles, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, uid=None, format=None):
        """
        Update the user profile with the given UID.
        Args:
            request (Request): The HTTP request object containing the data to update the user profile.
            uid (int, optional): The unique identifier of the user profile to update. Defaults to None.
            format (str, optional): The format of the request data. Defaults to None.
        Returns:
            Response: A Response object with the updated user profile data if successful,
                      or an error message with the appropriate HTTP status code.
        Raises:
            HTTP_404_NOT_FOUND: If the user profile with the given UID is not found.
            HTTP_403_FORBIDDEN: If the requesting user does not have permission to update the profile.
            HTTP_400_BAD_REQUEST: If the provided data is invalid.
        """
        userprofile = self.get_user_profile(uid)
        user = request.user

        if not userprofile:
            return Response({'detail': 'Benutzerprofil nicht gefunden'},
                            status=status.HTTP_404_NOT_FOUND)

        if not userprofile.user.id or userprofile.user.id != user.id:
            return Response(
                {'detail': 'Zugriff verweigert.'}, status=status.HTTP_403_FORBIDDEN)

        serializer = UserProfileSerializer(userprofile, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response({'detail': serializer.errors},
                        status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, uid=None, format=None):
        """
        Partially updates a user profile.
        Args:
            request (Request): The HTTP request object containing the data for the update.
            uid (int, optional): The user ID of the profile to update. Defaults to None.
            format (str, optional): The format of the request. Defaults to None.
        Returns:
            Response: A Response object containing the updated user profile data if successful,
                      or an error message with the appropriate HTTP status code if not.
        Raises:
            HTTP_404_NOT_FOUND: If the user profile is not found.
            HTTP_403_FORBIDDEN: If the requesting user does not have permission to update the profile.
            HTTP_400_BAD_REQUEST: If the provided data is invalid.
        """
        userprofile = self.get_user_profile(uid)
        user = request.user

        if not userprofile:
            return Response({'detail': 'Benutzerprofil nicht gefunden'},
                            status=status.HTTP_404_NOT_FOUND)

        if not userprofile.user.id or userprofile.user.id != user.id:
            return Response(
                {'detail': 'Zugriff verweigert.'}, status=status.HTTP_403_FORBIDDEN)

        serializer = UserProfileSerializer(
            userprofile, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response({'detail': serializer.errors},
                        status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, uid=None, format=None):
        """
        Deletes a user and their profile.
        Args:
            request (Request): The HTTP request object.
            uid (int, optional): The unique identifier of the user to be deleted. Defaults to None.
            format (str, optional): The format of the response. Defaults to None.
        Returns:
            Response: A response object with a status code indicating the result of the delete operation.
                - 204 No Content: If the user and their profile were successfully deleted.
                - 403 Forbidden: If the requesting user is not staff and does not match the user ID to be deleted.
                - 404 Not Found: If the user with the specified ID does not exist.
        """
        if not request.user.is_staff and request.user.id != uid:
            return Response({'detail': 'Zugriff verweigert'},
                            status=status.HTTP_403_FORBIDDEN)

        try:
            user = User.objects.get(pk=uid)
            user.delete()
            return Response({'detail': 'Benutzer und Benutzerprofil erfolgreich gelöscht.'},
                            status=status.HTTP_204_NO_CONTENT)
        except User.DoesNotExist:
            return Response({'detail': 'Benutzer nicht gefunden'},
                            status=status.HTTP_404_NOT_FOUND)


class UserRegister_View(APIView):
    """
    API view to register a new user.
    """

    def post(self, request):
        """
        Handle POST request for user registration.
        This method handles the registration of a new user. It validates the provided
        registration data, creates a new user, assigns a user profile type, generates
        an authentication token, and returns the token along with user details.
        Args:
            request (Request): The HTTP request object containing registration data.
        Returns:
            Response: A Response object containing the authentication token, username,
                      email, and user ID if registration is successful, or an error
                      message if validation fails.
        """
        username = request.data.get('username')
        email = request.data.get('email')
        password = request.data.get('password')
        repeated_password = request.data.get('repeated_password')
        type = request.data.get('type', 'customer')

        error_message_list = self.validate_registration_data(
            username, email, password, repeated_password)
        if error_message_list:
            return Response({'detail': error_message_list}, status=status.HTTP_400_BAD_REQUEST)

        user = User.objects.create_user(
            username=username, email=email, password=password)
        user.userprofile.type = type
        user.userprofile.save()

        token = Token.objects.get(user=user)

        return Response({
            'token': token.key,
            'username': user.username,
            'email': user.email,
            'user_id': user.id,
        }, status=status.HTTP_201_CREATED)

    def validate_registration_data(self, username, email, password, repeated_password):
        """
        Validates the registration data provided by the user.
        Args:
            username (str): The username provided by the user.
            email (str): The email address provided by the user.
            password (str): The password provided by the user.
            repeated_password (str): The repeated password provided by the user.
        Returns:
            list: A list of error messages, if any validation checks fail. 
                  If the list is empty, the registration data is valid.
        """
        error_message_list = []

        if not username or not email or not password or not repeated_password:
            error_message_list.append(
                'Benutzername, E-Mail, Passwort und wiederholtes Passwort sind erforderlich.')

        if password != repeated_password:
            error_message_list.append(
                'Das Passwort ist nicht gleich mit dem wiederholten Passwort')

        if User.objects.filter(username=username).exists():
            error_message_list.append(
                'Dieser Benutzername ist bereits vergeben.')

        if User.objects.filter(email=email).exists():
            error_message_list.append(
                'Diese E-Mail-Adresse wird bereits verwendet.')

        return error_message_list


class UserLogin_View(APIView):
    """
    API view to log in a user.
    """

    def post(self, request):
        """
        Handle POST request for user authentication.
        This method authenticates a user based on the provided username and password.
        If the username or password is missing, it returns a 400 Bad Request response with an error message.
        If the user does not exist, it returns a 404 Not Found response with an error message.
        If the authentication is successful, it returns a 200 OK response with the user's token, username, email, and user ID.
        If the authentication fails, it returns a 400 Bad Request response with an error message.
        Args:
            request (Request): The HTTP request object containing the username and password.
        Returns:
            Response: A DRF Response object with the appropriate status code and data.
        """
        username = request.data.get('username')
        password = request.data.get('password')

        error_message_list = []

        if not username or not password:
            error_message_list.append(
                'Benutzername and Password sind erforderlich.')
            return Response(
                {'detail': error_message_list},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            User.objects.get(username=username)
        except User.DoesNotExist:
            error_message_list.append('Benutzer existiert nicht.')
            return Response(
                {'detail': error_message_list},
                status=status.HTTP_404_NOT_FOUND
            )

        user = authenticate(username=username, password=password)
        if user is not None:
            token = Token.objects.get(user=user)
            return Response({
                'token': token.key,
                'username': user.username,
                'email': user.email,
                'user_id': user.id
            }, status=status.HTTP_200_OK)
        else:
            return Response(
                {'detail': 'Falsche Anmeldeinformationen oder ungültige Eingabe.'},
                status=status.HTTP_400_BAD_REQUEST
            )


class UserLogout_View(APIView):
    """
    API view to log out a user.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """
        Handle POST request to log out a user by deleting their authentication token.

        Args:
            request (Request): The HTTP request object containing user information.

        Returns:
            Response: A response indicating the result of the logout operation.
                - 200 OK: If the token was successfully deleted.
                - 400 Bad Request: If the token does not exist.
        """
        try:
            token = Token.objects.get(user=request.user)
            token.delete()
            return Response({'detail': 'Benutzer erfolgreich abgemeldet.'}, status=status.HTTP_200_OK)
        except Token.DoesNotExist:
            return Response({'detail': 'Token existiert nicht.'}, status=status.HTTP_400_BAD_REQUEST)
