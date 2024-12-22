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
        if type:
            userprofiles = UserProfile.objects.filter(type=type)
            serializer = UserProfileTypeSerializer(userprofiles, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response({'status': 'error', 'message': 'Type is required.'}, status=status.HTTP_400_BAD_REQUEST)


class UserProfile_View(APIView):
    """
    API view to retrieve, update, or delete user profiles.
    """
    permission_classes = [IsAuthenticated]

    def get_user_profile(self, uid):
        """
        Helper method to retrieve a user profile based on user ID.
        """
        try:
            user = User.objects.get(pk=uid)
            return UserProfile.objects.get(user=user)
        except (User.DoesNotExist, UserProfile.DoesNotExist):
            return None

    def get(self, request, uid=None, format=None):
        """
        Retrieve a user profile or all user profiles if no UID is provided.
        """
        if uid:
            userprofile = self.get_user_profile(uid)
            if not userprofile:
                return Response({'status': 'error', 'message': 'User Profile not found'},
                                status=status.HTTP_404_NOT_FOUND)
            serializer = UserProfileSerializer(userprofile)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            userprofiles = UserProfile.objects.all()
            serializer = UserProfileSerializer(userprofiles, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, uid=None, format=None):
        """
        Fully update a user profile.
        """
        userprofile = self.get_user_profile(uid)
        if not userprofile:
            return Response({'status': 'error', 'message': 'User Profile not found'},
                            status=status.HTTP_404_NOT_FOUND)
        serializer = UserProfileSerializer(userprofile, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response({'status': 'error', 'message': serializer.errors},
                        status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, uid=None, format=None):
        """
        Partially update a user profile.
        """
        userprofile = self.get_user_profile(uid)
        if not userprofile:
            return Response({'status': 'error', 'message': 'User Profile not found'},
                            status=status.HTTP_404_NOT_FOUND)
        serializer = UserProfileSerializer(
            userprofile, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response({'status': 'error', 'message': serializer.errors},
                        status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, uid=None, format=None):
        """
        Delete a user and their profile.
        """
        if not request.user.is_staff and request.user.id != uid:
            return Response({'status': 'error', 'message': 'Permission denied'},
                            status=status.HTTP_403_FORBIDDEN)

        try:
            user = User.objects.get(pk=uid)
            user.delete()
            return Response({'status': 'success', 'message': 'User and User Profile deleted successfully.'},
                            status=status.HTTP_204_NO_CONTENT)
        except User.DoesNotExist:
            return Response({'status': 'error', 'message': 'User not found'},
                            status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'status': 'error', 'message': f'Error: {str(e)}'},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class UserRegister_View(APIView):
    """
    API view to register a new user.
    """
    # permission_classes = [AllowAny]

    def post(self, request):
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

        token = Token.objects.create(user=user)

        return Response({
            'token': token.key,
            'username': user.username,
            'email': user.email,
            'user_id': user.id,
        }, status=status.HTTP_201_CREATED)

    def validate_registration_data(self, username, email, password, repeated_password):
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
    # permission_classes = [AllowAny]

    def post(self, request):
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
                {'message': error_message_list},
                status=status.HTTP_404_NOT_FOUND
            )

        user = authenticate(username=username, password=password)
        if user is not None:
            token, created = Token.objects.get_or_create(user=user)
            return Response({
                'token': token.key,
                'username': user.username,
                'email': user.email,
                'user_id': user.id
            }, status=status.HTTP_200_OK)
        else:
            return Response(
                {'detail': 'Falsche Anmeldeinformationen oder ungültige Eingabe.'},
                status=status.HTTP_401_UNAUTHORIZED
            )


class UserLogout_View(APIView):
    """
    API view to log out a user.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            token = Token.objects.get(user=request.user)
            token.delete()
            return Response({'detail': 'User logged out successfully.'}, status=status.HTTP_200_OK)
        except Token.DoesNotExist:
            return Response({'detail': 'Token does not exist.'}, status=status.HTTP_400_BAD_REQUEST)
