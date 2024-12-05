from django.urls import path

from user_auth_app.api.views import UserRegister_View, UserLogin_View, UserLogout_View, UserProfile_View


urlpatterns = [
    path('profile/', UserProfile_View.as_view(), name='profile'),
    path('register/', UserRegister_View.as_view(), name='register'),
    path('login/', UserLogin_View.as_view(), name='login'),
    path('logout/', UserLogout_View.as_view(), name='logout'),
    path('profile/<uid>/', UserProfile_View.as_view(), name='profile')
]
