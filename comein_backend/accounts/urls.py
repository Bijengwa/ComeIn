# accounts/urls.py or auth/urls.py
from django.urls import path
from .views import RegisterView, LoginView,DashboardView,LogoutView, CustomTokenObtainPairSerializer,VerifyEmailView

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('dashboard/', DashboardView.as_view(), name='dashboard'),
    path('logout/', LogoutView.as_view(), name= 'logout'),
    path('verify-email/<uidb64>/<token>/', VerifyEmailView.as_view(), name='verify_email'),
    
]
