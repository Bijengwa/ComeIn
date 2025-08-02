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
import africastalking

from .models import CustomUser, PhoneOTP
from .serializers import UserSerializer

User = get_user_model()
MAX_FAILED_ATTEMPTS = 5


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        # Handle new user registration and send verification
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        user.is_active = False  # Prevent login before verification
        user.save()

        if user.email:
            self.send_verification_email(user)

        if user.phone_number:
            self.send_phone_otp(user.phone_number)

        return Response({
            "message": "Account created. Verify email or phone to activate account."
        }, status=status.HTTP_201_CREATED)

    def send_verification_email(self, user):
        # Send an email with verification link
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
        # Create or update OTP record for the given phone
        otp, _ = PhoneOTP.objects.get_or_create(phone_number=phone_number)
        otp.otp = str(random.randint(100000, 999999))
        otp.created_at = timezone.now()
        otp.is_verified = False
        otp.save()

        print(f"DEBUG OTP to {phone_number}: {otp.otp}")

#initialize Africa's Talking SDK once using the settings.py credentials 
africastalking.initialize(
    username=settings.AFRICASTALKING_USERNAME,
    api_key= settings.AFRICASTALKING_API_KEY
)
 
sms = africastalking.SMS
class SendPhoneOTPView(APIView):
    def post(self, request):
        # Send or resend OTP manually to a phone number
        phone_number = request.data.get("phone_number")

        if not phone_number:
            return Response({"error": "Phone number is required."}, status=status.HTTP_400_BAD_REQUEST)

        otp_obj, _ = PhoneOTP.objects.get_or_create(phone_number=phone_number)
        otp_obj.otp = str(random.randint(100000, 999999))
        otp_obj.created_at = timezone.now()
        otp_obj.is_verified = False
        otp_obj.save()

        #international format of phone number
        if phone_number.startwith("0"):
            phone_number = "+255" +phone_number[1:]

        try:
            sms.send(
                message=f"your OTP is {otp_obj.otp}",
                recepients=[phone_number]
            )    

            return Response({"message": "OTP sent successfully."}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error":str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR) 

class VerifyEmailView(APIView):
    def get(self, request, uidb64, token):
        # Verify email using uid and token
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


class VerifyPhoneOTPView(APIView):
    def post(self, request):
        # Confirm if the given OTP is valid for the phone number
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


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        # Extend JWT with additional user info
        token = super().get_token(user)
        token["email"] = user.email
        token["full_name"] = user.full_name
        token["phone_number"] = user.phone_number
        return token


class LoginView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        # Authenticate user and issue JWT tokens
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

        user.failed_login_attempts = 0
        user.save()

        refresh = RefreshToken.for_user(user)
        return Response({
            "user": UserSerializer(user).data,
            "refresh": str(refresh),
            "access": str(refresh.access_token),
        })


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # Logout by blacklisting the refresh token
        try:
            refresh_token = request.data.get("refresh")
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({"message": "Logged out successfully"})
        except Exception as e:
            return Response({"error": str(e)}, status=400)


class DashboardView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Return dashboard data for logged-in user
        user = request.user
        return Response({
            "message": "Welcome to your dashboard!",
            "user": {
                "email": user.email,
                "full_name": user.full_name,
            }
        })


class ResendVerificationView(APIView):
    def post(self, request):
        # Allow user to resend verification email or phone OTP
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


class SendResetLinkView(APIView):
    def post(self, request):
        # Send password reset email or OTP to phone
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



class ResetPasswordView(APIView):
    def post(self, request):
        email = request.data.get("email")
        phone = request.data.get("phone_number")
        new_password = request.data.get("new_password")
        confirm_password = request.data.get("confirm_password")
        uidb64 = request.data.get("uidb64")
        token = request.data.get("token")
        otp = request.data.get("otp")

        if new_password != confirm_password:
            return Response({"error": "Passwords do not match"},status=404)

        
        #if resetting via email 
        if email and uidb64 and token:
            try:
                uid = force_str(urlsafe_base64_decode(uidb64))
                user = CustomUser.objects.get(pk=uid, email=email)

                if default_token_generator.check_token(user, token):
                    user.set_password(new_password)
                    user.save()
                    return Response({"message": "Password reset successfully"})
                
                else:
                    return Response({"error":"Invalid or expired token"}, status=404)

            except CustomUser.DoesNotExit:
                return Response({"error": "User not found"}, status=404)  



        #if resetting via phone OTP
        if phone and otp:
            try:
                phone_otp = PhoneOTP.objects.get(phone_number=phone, otp=otp)  
                 
                if phone_otp.otp == otp and not phone_otp.is_expired():
                    user = CustomUser.objects.get(phone_number=phone) 
                    user.set_password(new_password)
                    user.save()
                    return Response({"message": "password reset successfully"})
                
                else:
                    return Response({"error": "Invalid or expired OTP"})
                
            except(phone_otp.DoesNotExist, CustomUser.DoesNotExist):    
                return Response({"error": "User or OTP not found"}, status=404)
            

        return Response({"error": "Missing required fields"},status=400)   





class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]    

    def post(self, request):
        user = request.user
        current_password = request.data.get("current_password")
        new_password = request.data.get(new_password)
        confirm_password = request.data.get(confirm_password) 

        #check if current password is correct 
        if not user.check_password(current_password):
            return Response({"error": "current password is incorrect"},status=400)
        

        #check if new password match
        if new_password != confirm_password:
            return Response({"error": "New password do not match!"},status=400)
        
        #set and save new password 
        user.set_password(new_password)
        user.save()

        return Response({"messages": "password changed successfully"},status=400)