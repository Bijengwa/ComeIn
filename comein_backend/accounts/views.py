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
from django.db import IntegrityError
from django.utils import timezone

import random
import africastalking

from .models import CustomUser, PhoneOTP
from .serializers import UserSerializer
def maybe_activate_user(user):
    # Activate user account if both email and phone number are verified 
    phone_ok = False

    #check if phone number is verified 
    if user.phone_number:
        phone_ok = PhoneOTP.objects.filter(
            phone_number=user.phone_number,
            is_verified=True
        ).exists()
    
    # activate if both email and phone are verified 
    if user.is_verified and phone_ok and not user.is_active:
        user.is_active = True
        user.save()
        print(f" ✅ User {user.email} activated successfully.")

    else:
        print("⚠️ Activation skipped: either email or phone not verified or already active.")    



User = get_user_model()
MAX_FAILED_ATTEMPTS = 5


def maybe_activate_user(user):
    # Activate the 
    phone_ok = False
    if user.phone_number:
        phone_ok = PhoneOTP.objects.filter(
            phone_number=user.phone_number,
            is_verified=True
        ).exists()

    if user.is_verified and phone_ok and not user.is_active:
        user.is_active = True
        user.save()

#view for handling user registration email + phone verification 
class RegisterView(generics.CreateAPIView):
    #set queryset and serializer for this view 
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        # create a serializer instance with incoming data
        serializer = self.get_serializer(data=request.data)

        try:
            #validate serializer data(raise exception if data is invalid)
            serializer.is_valid(raise_exception=True)

            #save the user instance (creates the user)
            user = serializer.save()

            #mark the user as inactive until email and phone are verified 
            user.is_active = False

            user.save()

            #send email verification link if email is provided 
            if user.email:
              self.send_verification_email(user)

            #send phone OTP if phone number is provided 
            if user.phone_number:
               self.send_phone_otp(user.phone_number)
            
            #return sucess response to frontend 
            return Response(
                {"message": "Account created. Verify email and phone to activate account."},
                status=status.HTTP_201_CREATED
            )
        
        #catch duplicate entries(like existing  phone number or email )
        except IntegrityError:
            return Response({"error": "phone number or email already registered"}, status=status.HTTP_400_BAD_REQUEST)

    def send_verification_email(self, user):
        # Build and send an email verification link containing uid and token
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
        # Generate or refresh a 6-digit OTP and persist it for the given phone
        otp, _ = PhoneOTP.objects.get_or_create(phone_number=phone_number)
        otp.otp = str(random.randint(100000, 999999))
        otp.created_at = timezone.now()
        otp.is_verified = False
        otp.save()
        
        #convert to international format 
        if phone_number.startswith("0"):
            phone_number = "+255" + phone_number[1:]

        #remove spaces 
        phone_number = phone_number.replace(" ", "")


        try:
            sms.send(
                message = f"Your OTP is {otp.otp}",
                recipients =[phone_number]
            )  

        except Exception as e:
            print(f"Error  sending SMS {e}")      


# Initialize Africa's Talking SDK once using settings.py credentials
africastalking.initialize(
    username=settings.AFRICASTALKING_USERNAME,
    api_key=settings.AFRICASTALKING_API_KEY
)
sms = africastalking.SMS


class SendPhoneOTPView(APIView):
    def post(self, request):
        # Generate OTP and send via Africa's Talking SMS API
        phone_number = request.data.get("phone_number")

        if not phone_number:
            return Response({"error": "Phone number is required."}, status=status.HTTP_400_BAD_REQUEST)

        otp_obj, _ = PhoneOTP.objects.get_or_create(phone_number=phone_number)
        otp_obj.otp = str(random.randint(100000, 999999))
        otp_obj.created_at = timezone.now()
        otp_obj.is_verified = False
        otp_obj.save()

        # Convert local TZ number (07..., 06...) to E.164 (+255...)
        if phone_number.startswith("0"):
            phone_number = "+255" + phone_number[1:]

            #remove spaces
        phone_number = phone_number.replace(" ", "")


        try:
            # Send SMS with the OTP to the destination number
            sms.send(
                message=f"Your OTP is {otp_obj.otp}",
                recipients=[phone_number]
            )
            return Response({"message": "OTP sent successfully."}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class VerifyEmailView(APIView):
    def get(self, request, uidb64, token):
        # Decode the uid, find the user, validate token, then mark email verified
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = CustomUser.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, CustomUser.DoesNotExist):
            return Response({"error": "Invalid link"}, status=status.HTTP_400_BAD_REQUEST)

        if default_token_generator.check_token(user, token):
            user.is_verified = True  # email verified
            user.save()
            # Try activation only after email is verified; phone must also be verified
            maybe_activate_user(user)
            return Response({"message": "Email verified!"}, status=status.HTTP_200_OK)

        return Response({"error": "Invalid or expired token"}, status=status.HTTP_400_BAD_REQUEST)


class VerifyPhoneOTPView(APIView):
    def post(self, request):
        # Validate OTP for the provided phone and, if valid, attempt activation
        phone = request.data.get("phone_number")
        otp = request.data.get("otp")

        #basic validation
        if not phone or not otp:
            return Response({"error": "Phone number and OTP are required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Retrieve the OTP record from the database
            phone_otp = PhoneOTP.objects.get(phone_number=phone)

            # check if the OTP matches and not expired             
            if phone_otp.otp == otp and not phone_otp.is_expired():
                phone_otp.is_verified = True
                phone_otp.save()
                
                try:
                    # Try to find the user by phone number
                    user = CustomUser.objects.get(phone_number=phone)
                    
                    #attempts user activation if both phone and email are verified 
                    maybe_activate_user(user)

                    return Response({"message": "Phone number verified successfully!"}, status=status.HTTP_200_OK)
                
                except CustomUser.DoesNotExist:
                    return Response({"error":"user with this phone number does not exist"},status=status.HTTP_404_NOT_FOUND)
            
            #if OTP is 
            return Response({"error": "Invalid or expired OTP"}, status=status.HTTP_400_BAD_REQUEST)

        except PhoneOTP.DoesNotExist:
            return Response({"error": "OTP not sent or phone number not found"}, status=status.HTTP_404_NOT_FOUND)


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        # Add extra user fields to the JWT payload for convenience on the client
        token = super().get_token(user)
        token["email"] = user.email
        token["full_name"] = getattr(user, "full_name", "")
        token["phone_number"] = getattr(user, "phone_number", "")
        return token


class LoginView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        # Authenticate by email/password, enforce lockout, and require activation before issuing tokens
        email = request.data.get("email")
        password = request.data.get("password")

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)

        if user.failed_login_attempts >= MAX_FAILED_ATTEMPTS:
            return Response({"error": "Account locked. Too many failed attempts."}, status=status.HTTP_403_FORBIDDEN)

        if not user.check_password(password):
            user.failed_login_attempts = F("failed_login_attempts") + 1
            user.save(update_fields=["failed_login_attempts"])
            return Response({"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)

        if not user.is_active:
            return Response({"error": "Account not active. Complete email and phone verification."},
                            status=status.HTTP_403_FORBIDDEN)

        user.failed_login_attempts = 0
        user.save(update_fields=["failed_login_attempts"])

        refresh = RefreshToken.for_user(user)
        return Response(
            {
                "user": UserSerializer(user).data,
                "refresh": str(refresh),
                "access": str(refresh.access_token),
            },
            status=status.HTTP_200_OK
        )


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # Blacklist the provided refresh token to log the user out
        try:
            refresh_token = request.data.get("refresh")
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({"message": "Logged out successfully"}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class DashboardView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Return simple profile data for the authenticated user
        user = request.user
        return Response(
            {
                "message": "Welcome to your dashboard!",
                "user": {
                    "email": user.email,
                    "full_name": getattr(user, "full_name", ""),
                }
            },
            status=status.HTTP_200_OK
        )


class ResendVerificationView(APIView):
    def post(self, request):
        # Resend either email verification link or phone OTP based on payload
        email = request.data.get("email")
        phone = request.data.get("phone_number")

        if email:
            try:
                user = User.objects.get(email=email)
                RegisterView().send_verification_email(user)
                return Response({"message": "Verification email sent"}, status=status.HTTP_200_OK)
            except User.DoesNotExist:
                return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

        if phone:
            try:
                user = User.objects.get(phone_number=phone)
                RegisterView().send_phone_otp(phone)
                return Response({"message": "OTP resent"}, status=status.HTTP_200_OK)
            except User.DoesNotExist:
                return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

        return Response({"error": "Provide email or phone_number"}, status=status.HTTP_400_BAD_REQUEST)


class SendResetLinkView(APIView):
    def post(self, request):
        # Initiate password reset via email link or phone OTP
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
                    recipient_list=[user.email],
                    fail_silently=False,
                )
                return Response({"message": "Reset link sent to email"}, status=status.HTTP_200_OK)
            except User.DoesNotExist:
                return Response({"error": "Email not found"}, status=status.HTTP_404_NOT_FOUND)

        if phone:
            try:
                otp, _ = PhoneOTP.objects.get_or_create(phone_number=phone)
                otp.otp = str(random.randint(100000, 999999))
                otp.created_at = timezone.now()
                otp.is_verified = False
                otp.save()
                print(f"DEBUG RESET OTP for {phone}: {otp.otp}")
                return Response({"message": "Reset OTP sent to phone"}, status=status.HTTP_200_OK)
            except Exception:
                return Response({"error": "Phone number invalid"}, status=status.HTTP_400_BAD_REQUEST)

        return Response({"error": "Provide phone or email"}, status=status.HTTP_400_BAD_REQUEST)


class ResetPasswordView(APIView):
    def post(self, request):
        # Complete password reset using either email token or phone OTP
        email = request.data.get("email")
        phone = request.data.get("phone_number")
        new_password = request.data.get("new_password")
        confirm_password = request.data.get("confirm_password")
        uidb64 = request.data.get("uidb64")
        token = request.data.get("token")
        otp = request.data.get("otp")

        if new_password != confirm_password:
            return Response({"error": "Passwords do not match"}, status=status.HTTP_400_BAD_REQUEST)

        if email and uidb64 and token:
            try:
                uid = force_str(urlsafe_base64_decode(uidb64))
                user = CustomUser.objects.get(pk=uid, email=email)
                if default_token_generator.check_token(user, token):
                    user.set_password(new_password)
                    user.save()
                    return Response({"message": "Password reset successfully via email"}, status=status.HTTP_200_OK)
                return Response({"error": "Invalid or expired token"}, status=status.HTTP_400_BAD_REQUEST)
            except CustomUser.DoesNotExist:
                return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

        if phone and otp:
            try:
                phone_otp = PhoneOTP.objects.get(phone_number=phone)
                if phone_otp.otp == otp and not phone_otp.is_expired():
                    user = CustomUser.objects.get(phone_number=phone)
                    user.set_password(new_password)
                    user.save()
                    return Response({"message": "Password reset successfully via phone"}, status=status.HTTP_200_OK)
                return Response({"error": "Invalid or expired OTP"}, status=status.HTTP_400_BAD_REQUEST)
            except (PhoneOTP.DoesNotExist, CustomUser.DoesNotExist):
                return Response({"error": "User or OTP not found"}, status=status.HTTP_404_NOT_FOUND)

        return Response({"error": "Missing required fields"}, status=status.HTTP_400_BAD_REQUEST)


class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # Allow logged-in users to change password using their current password
        user = request.user
        current_password = request.data.get("current_password")
        new_password = request.data.get("new_password")
        confirm_password = request.data.get("confirm_password")

        if not user.check_password(current_password):
            return Response({"error": "Current password is incorrect"}, status=status.HTTP_400_BAD_REQUEST)

        if new_password != confirm_password:
            return Response({"error": "New passwords do not match"}, status=status.HTTP_400_BAD_REQUEST)

        user.set_password(new_password)
        user.save()
        return Response({"message": "Password changed successfully"}, status=status.HTTP_200_OK)
