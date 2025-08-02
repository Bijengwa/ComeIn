from pathlib import Path
from datetime import timedelta
from django.conf import settings

# Define the base directory of the project
BASE_DIR = Path(__file__).resolve().parent.parent

# Secret key for cryptographic signing (keep it hidden in production)
SECRET_KEY = 'django-insecure-your-secret-key-here'

# Enable debug mode (set to False in production)
DEBUG = True

# Define allowed hosts for deployment
ALLOWED_HOSTS = []

# Set the custom user model
AUTH_USER_MODEL = 'accounts.CustomUser'

# Apps installed in this Django project
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Third-party apps
    'rest_framework',
    'rest_framework_simplejwt',
    'corsheaders',
    'rest_framework_simplejwt.token_blacklist',

    # Local apps
    'accounts',
]

# Middleware classes used by Django
MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',  # Allows cross-origin requests React 
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# Allow requests from any frontend (open CORS policy)
CORS_ALLOW_ALL_ORIGINS = True

# Root URL configuration
ROOT_URLCONF = 'buying_app.urls'

# Template engine configuration
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

# WSGI entry point for running the app
WSGI_APPLICATION = 'buying_app.wsgi.application'

# Default database configuration using SQLite
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Email configuration using Gmail SMTP (for sending verification emails)
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'altoanacrethus@gmail.com'  
EMAIL_HOST_PASSWORD = 'gnravinldjotxrks'  # Use app password or environment variable for safety
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER

# URL where email verification should point (e.g. your React frontend)
FRONTEND_URL = 'http://localhost:3000'

# Password validators to enforce strong password rules
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# Set language and time zone
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Static file configuration (CSS, JS, images)
STATIC_URL = 'static/'

# Set default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# REST Framework settings for authentication
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
}

#Africa's Talking settings
AFRICASTALKING_USERNAME = "sandbox"
AFRICASTALKING_API_KEY = "atsk_94e6e85607118ade091e220d90c961c02b45f96903e52951f2694a2a56aeb399d0149c77"

# JWT configuration for handling tokens
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=5),  # Token expires in 5 minutes
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),  # Refresh token valid for 1 day
    'ROTATE_REFRESH_TOKENS': True,  # Allow refresh token to rotate (generate new)
    'BLACKLIST_AFTER_ROTATION': False,  # Disable old token after rotation
    'AUTH_HEADER_TYPES': ('Bearer',),
}
