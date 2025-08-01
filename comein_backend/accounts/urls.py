from django.urls import path
from .views import (
    RegisterView,
    LoginView,
    LogoutView,
    DashboardView,
    VerifyEmailView,
    SendPhoneOTPView,
    VerifyPhoneOTPView,
    ResendVerificationView,
    SendResetLinkView
)
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('dashboard/', DashboardView.as_view(), name='dashboard'),

    path('verify-email/<uidb64>/<token>/', VerifyEmailView.as_view(), name='verify-email'),
    path('resend-verification/', ResendVerificationView.as_view(), name='resend-verification'),

    path('send-phone-otp/', SendPhoneOTPView.as_view(), name='send-otp'),
    path('verify-phone-otp/', VerifyPhoneOTPView.as_view(), name='verify-otp'),

    path('reset-password/', SendResetLinkView.as_view(), name='reset-password'),

    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
