from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

from user_auth_app.api.views import UserRegister_View, UserLogin_View, UserLogout_View, UserProfile_View, UserProfileType_View

urlpatterns = [
    path('api/registration/', UserRegister_View.as_view(), name='register'),
    path('api/login/', UserLogin_View.as_view(), name='login'),
    path('api/logout/', UserLogout_View.as_view(), name='logout'),
    path('api/profile/', UserProfile_View.as_view(), name='profile'),
    path('api/profile/<uid>/', UserProfile_View.as_view(), name='profile_detail'),
    path('api/profiles/<type>/', UserProfileType_View.as_view(), name='profiletype'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
