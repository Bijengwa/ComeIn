from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from django.contrib.auth import get_user_model
from .serializers import UserSerializer

User = get_user_model()

#  RegisterView handles new user registration with password confirmation
class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]  # Anyone can register

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        # Validate input
        serializer.is_valid(raise_exception=True)

        # Save new user
        user = serializer.save()

        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)

        # Respond with user info and tokens
        return Response({
            'user': UserSerializer(user).data,
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }, status=status.HTTP_201_CREATED)



# LoginView authenticates user with email + password
class LoginView(APIView):
    def post(self, request, *args, **kwargs):
        email = request.data.get('email')
        password = request.data.get('password')

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({"error": "Invalid email or password"},status=status.HTTP_401_UNAUTHORIZED)
            

        if not user.check_password(password):
            return Response({"error": "Invalid email or password"},status=status.HTTP_401_UNAUTHORIZED )
        

        if not user.is_active:
            return Response({"erroe": "User account is inactive"},status=status.HTTP_403_FORBIDDEN)   
        

        refresh = RefreshToken.for_user(user)
        return Response({
            'user': UserSerializer(user).data,
            'refresh': str(refresh),
            'access': str(refresh.access_token),

        }, status=status.HTTP_200_OK)