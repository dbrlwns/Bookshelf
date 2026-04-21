from django.urls import path

from . import views

urlpatterns = [
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('signup/', views.user_signup, name='register'),
    path('profile/', views.user_edit, name='profile_edit'),
    path('userinfo/', views.user_info, name='user_info'),
    path('userEdit/', views.user_edit, name='user_edit'),
]
