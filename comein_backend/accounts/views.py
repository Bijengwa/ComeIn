from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth import get_user_model
from django.conf import settings
from django.db.models import F
from django.utils import timezone
import random

from .models import CustomUser, PhoneOTP
from .serializers import UserSerializer

User = get_user_model()

#  Global setting for failed login limit
MAX_FAILED_ATTEMPTS = 5


#  Handles user registration and sends email + OTP
class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.save()
        user.is_active = False
        user.save()

        # Send both email and phone OTP if available
        if user.email:
            self.send_verification_email(user)
        if user.phone_number:
            self.send_phone_otp(user.phone_number)

        return Response({
            "message": "Account created. Verify email or phone to activate account."
        }, status=status.HTTP_201_CREATED)

    def send_verification_email(self, user):
        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        link = f"{settings.FRONTEND_URL}/verify-email/{uid}/{token}/"

        send_mail(
            subject="Verify your email",
            message=f"Click the link to verify your email: {link}",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False,
        )

    def send_phone_otp(self, phone_number):
        otp, _ = PhoneOTP.objects.get_or_create(phone_number=phone_number)
        otp.otp = str(random.randint(100000, 999999))
        otp.created_at = timezone.now()
        otp.is_verified = False
        otp.save()

        # TODO: Integrate SMS API like Infobip or Twilio
        print(f"DEBUG OTP to {phone_number}: {otp.otp}")


# Verifies email using the token and uid
class VerifyEmailView(APIView):
    def get(self, request, uidb64, token):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = CustomUser.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, CustomUser.DoesNotExist):
            return Response({"error": "Invalid link"}, status=400)

        if default_token_generator.check_token(user, token):
            user.is_verified = True
            user.is_active = True
            user.save()
            return Response({"message": "Email verified!"}, status=200)
        return Response({"error": "Invalid or expired token"}, status=400)


# Verifies phone OTP
class VerifyPhoneOTPView(APIView):
    def post(self, request):
        phone = request.data.get("phone_number")
        otp = request.data.get("otp")

        try:
            phone_otp = PhoneOTP.objects.get(phone_number=phone)
            if phone_otp.otp == otp and not phone_otp.is_expired():
                phone_otp.is_verified = True
                phone_otp.save()

                user = CustomUser.objects.get(phone_number=phone)
                user.is_verified = True
                user.is_active = True
                user.save()

                return Response({"message": "Phone number verified!"})
            return Response({"error": "Invalid or expired OTP"}, status=400)
        except PhoneOTP.DoesNotExist:
            return Response({"error": "OTP not sent or phone number not found"}, status=404)


#  Serializer that includes custom JWT claims
class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token["email"] = user.email
        token["full_name"] = user.full_name
        token["phone_number"] = user.phone_number
        return token


#Login view with account lock + verification checks
class LoginView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        email = request.data.get("email")
        password = request.data.get("password")

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({"error": "Invalid credentials"}, status=401)

        if user.failed_login_attempts >= MAX_FAILED_ATTEMPTS:
            return Response({"error": "Account locked. Too many failed attempts."}, status=403)

        if not user.check_password(password):
            user.failed_login_attempts = F("failed_login_attempts") + 1
            user.save()
            return Response({"error": "Invalid credentials"}, status=401)

        if not user.is_verified:
            return Response({"error": "Verify email or phone first"}, status=403)

        # Reset failed login count on success
        user.failed_login_attempts = 0
        user.save()

        refresh = RefreshToken.for_user(user)
        return Response({
            "user": UserSerializer(user).data,
            "refresh": str(refresh),
            "access": str(refresh.access_token),
        })


#  Allows users to logout and blacklist their refresh token
class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data.get("refresh")
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({"message": "Logged out successfully"})
        except Exception as e:
            return Response({"error": str(e)}, status=400)


#  View for authenticated dashboard
class DashboardView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        return Response({
            "message": "Welcome to your dashboard!",
            "user": {
                "email": user.email,
                "full_name": user.full_name,
            }
        })


#  Resends email or OTP depending on user contact
class ResendVerificationView(APIView):
    def post(self, request):
        email = request.data.get("email")
        phone = request.data.get("phone_number")

        if email:
            try:
                user = User.objects.get(email=email)
                RegisterView().send_verification_email(user)
                return Response({"message": "Verification email sent"})
            except User.DoesNotExist:
                return Response({"error": "User not found"}, status=404)

        elif phone:
            try:
                user = User.objects.get(phone_number=phone)
                RegisterView().send_phone_otp(phone)
                return Response({"message": "OTP resent"})
            except User.DoesNotExist:
                return Response({"error": "User not found"}, status=404)

        return Response({"error": "Provide email or phone_number"}, status=400)


#  Sends OTP or email to reset password
class SendResetLinkView(APIView):
    def post(self, request):
        email = request.data.get("email")
        phone = request.data.get("phone_number")

        if email:
            try:
                user = User.objects.get(email=email)
                token = default_token_generator.make_token(user)
                uid = urlsafe_base64_encode(force_bytes(user.pk))
                link = f"{settings.FRONTEND_URL}/reset-password/{uid}/{token}/"
                send_mail(
                    subject="Reset your password",
                    message=f"Click to reset password: {link}",
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[user.email]
                )
                return Response({"message": "Reset link sent to email"})
            except User.DoesNotExist:
                return Response({"error": "Email not found"}, status=404)

        elif phone:
            try:
                otp, _ = PhoneOTP.objects.get_or_create(phone_number=phone)
                otp.otp = str(random.randint(100000, 999999))
                otp.created_at = timezone.now()
                otp.save()
                print(f"DEBUG RESET OTP for {phone}: {otp.otp}")
                return Response({"message": "Reset OTP sent to phone"})
            except Exception:
                return Response({"error": "Phone number invalid"}, status=404)

        return Response({"error": "Provide phone or email"}, status=400)
