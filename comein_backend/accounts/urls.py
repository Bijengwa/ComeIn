from django.urls import path
from .views import (
    RegisterView,
    LoginView,
    LogoutView,
    DashboardView,
    VerifyEmailView,
    SendPhoneOTPView,
    VerifyPhoneOTPView,
    ResendEmailVerificationView,
    ResendPhoneOTPView,
    ResetPasswordView,
    TokenRefreshView
)

urlpatterns = [
    path('auth/register/', RegisterView.as_view(), name='register'),
    path('auth/login/', LoginView.as_view(), name='login'),
    path('auth/logout/', LogoutView.as_view(), name='logout'),
    path('auth/dashboard/', DashboardView.as_view(), name='dashboard'),

    path('auth/verify-email/<uidb64>/<token>/', VerifyEmailView.as_view(), name='verify-email'),
    path('auth/resend-email/', ResendEmailVerificationView.as_view(), name='resend-email'),

    path('auth/send-phone-otp/', SendPhoneOTPView.as_view(), name='send-otp'),
    path('auth/verify-phone-otp/', VerifyPhoneOTPView.as_view(), name='verify-otp'),
    path('auth/resend-otp/', ResendPhoneOTPView.as_view(), name='resend-otp'),

    path('auth/reset-password/', ResetPasswordView.as_view(), name='reset-password'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token-refresh'),
]
