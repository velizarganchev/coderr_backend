from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

from user_auth_app.api.views import UserRegister_View, UserLogin_View, UserLogout_View, UserProfile_View, UserProfileType_View

urlpatterns = [
    # URL pattern for user registration
    path('api/registration/', UserRegister_View.as_view(), name='register'),
    # URL pattern for user login
    path('api/login/', UserLogin_View.as_view(), name='login'),
    # URL pattern for user logout
    path('api/logout/', UserLogout_View.as_view(), name='logout'),
    # URL pattern for user profile
    path('api/profile/', UserProfile_View.as_view(), name='profile'),
    # URL pattern for user profile detail
    path('api/profile/<uid>/', UserProfile_View.as_view(), name='profile_detail'),
    # URL pattern for user profile type
    path('api/profiles/<type>/', UserProfileType_View.as_view(), name='profiletype'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
