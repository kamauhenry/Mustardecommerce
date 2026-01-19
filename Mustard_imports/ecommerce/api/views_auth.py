from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token
from django.contrib.auth import login, logout, authenticate, get_user_model, update_session_auth_hash
from django.core.mail import send_mail
from django.core.cache import cache
from django.core.cache.backends.base import InvalidCacheBackendError
from django.conf import settings
from django.http import JsonResponse
from django.utils import timezone
from django.utils.crypto import get_random_string
from django.views.decorators.csrf import csrf_exempt
from google.oauth2 import id_token
from google.auth.transport.requests import Request
import random
import logging
import time

from ..models import User, OTP
from .serializers import (
    UserSerializer, UserUpdateSerializer,
    LoginSerializer, RegisterSerializer, AdminLoginSerializer, AdminRegisterSerializer
)
from .permissions import IsOwnerOrAdmin, IsAdminUser

logger = logging.getLogger(__name__)
User = get_user_model()


class SendOTPView(APIView):
    permission_classes = [permissions.AllowAny]
    def post(self, request):
        email = request.data.get('email')
        try:
            user = User.objects.get(email=email)
            if not user.is_verified:
                otp = get_random_string(length=6, allowed_chars='0123456789')
                OTP.objects.create(user=user, code=otp)
                try:
                    send_mail(
                        'Your OTP',
                        f'Your OTP is {otp}',
                        'sales@mustardimports.co.ke',
                        [email],
                    )
                except Exception as e:
                    logger.error(f"Failed to send OTP email to {email}: {e}")
                    # Don't fail the API - OTP was created successfully
                return Response({'message': 'OTP sent'}, status=status.HTTP_200_OK)
            return Response({'message': 'User already verified'}, status=status.HTTP_400_BAD_REQUEST)
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)


class VerifyOTPView(APIView):
    permission_classes = [permissions.AllowAny]
    def post(self, request):
        email = request.data.get('email')
        otp = request.data.get('otp')
        try:
            user = User.objects.get(email=email)
            otp_obj = OTP.objects.get(user=user, otp=otp)
            user.is_verified = True
            user.save()
            otp_obj.delete()
            # Send welcome email after verification
            try:
                send_mail(
                    'Welcome to Our Platform',
                    'Your registration is complete. Welcome aboard!',
                    'sales@mustardimports.co.ke',
                    [email],
                )
            except Exception as e:
                logger.error(f"Failed to send welcome email to {email}: {e}")
                # Don't fail the API - verification was successful
            return Response({'message': 'OTP verified'}, status=status.HTTP_200_OK)
        except (User.DoesNotExist, OTP.DoesNotExist):
            return Response({'error': 'Invalid OTP'}, status=status.HTTP_400_BAD_REQUEST)


class ForgotPasswordView(APIView):
    permission_classes = [permissions.AllowAny]
    def post(self, request):
        email = request.data.get('email')
        try:
            user = User.objects.get(email=email)
            token = get_random_string(length=32)
            user.reset_token = token
            user.save()
            # Change this to point to the Vue frontend route
            reset_link = f'http://localhost:5173/reset-password/{token}'  # Adjust port if needed
            try:
                send_mail(
                    'Password Reset',
                    f'Click here to reset your password: {reset_link}\nIf you did not request this, please ignore this email.',
                    'sales@mustardimports.co.ke',
                    [email],
                )
            except Exception as e:
                logger.error(f"Failed to send password reset email to {email}: {e}")
                # Don't fail - token was saved successfully
        except User.DoesNotExist:
            pass  # Don't reveal if email exists
        return Response({'message': 'If the email exists, a reset link has been sent'}, status=status.HTTP_200_OK)


class ResetPasswordView(APIView):
    permission_classes = [permissions.AllowAny]
    @csrf_exempt
    def post(self, request, token):
        try:
            user = User.objects.get(reset_token=token)
            new_password = request.data.get('new_password')
            user.set_password(new_password)
            user.reset_token = None
            user.save()
            return Response({'message': 'Password reset successful'}, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({'error': 'Invalid token'}, status=status.HTTP_400_BAD_REQUEST)


class AdminRegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = AdminRegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            login(request, user)
            token, created = Token.objects.get_or_create(user=user)
            return Response({
                'message': 'Admin registration successful',
                'user_id': user.id,
                'username': user.username,
                'email': user.email,
                'user_type': user.user_type,
                'token': token.key,
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AdminLoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = AdminLoginSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            user = serializer.validated_data['user']
            login(request, user)
            token, created = Token.objects.get_or_create(user=user)
            return Response({
                'message': 'Admin login successful',
                'user_id': user.id,
                'username': user.username,
                'user_type': user.user_type,
                'token': token.key,
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request):
        if not request.user.is_authenticated:
            return Response({'message': 'Not logged in'}, status=status.HTTP_401_UNAUTHORIZED)
        if request.user.user_type != 'admin':
            return Response({'error': 'Only admins can use this endpoint'}, status=status.HTTP_403_FORBIDDEN)
        return Response({
            'message': 'Logged in as admin',
            'user_id': request.user.id,
            'username': request.user.username,
            'email': request.user.email,
            'user_type': request.user.user_type,
        }, status=status.HTTP_200_OK)


class AdminLogoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        if request.user.user_type != 'admin':
            return Response({'error': 'Only admins can use this endpoint'}, status=status.HTTP_403_FORBIDDEN)
        logout(request)
        return Response({'message': 'Admin logged out successfully'}, status=status.HTTP_200_OK)


class AdminProfileView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        if request.user.user_type != 'admin':
            return Response({'error': 'Only admins can access this endpoint'}, status=status.HTTP_403_FORBIDDEN)

        cache_key = f'admin_profile_{request.user.id}'
        try:
            cached_data = cache.get(cache_key)
            if cached_data:
                return Response(cached_data)
        except (InvalidCacheBackendError, Exception) as e:
            print(f"Cache error: {e}. Falling back to direct query.")

        serializer = UserSerializer(request.user)
        response_data = serializer.data

        try:
            cache.set(cache_key, response_data, timeout=60 * 5)  # Cache for 5 minutes
        except (InvalidCacheBackendError, Exception) as e:
            print(f"Failed to cache response: {e}")

        return Response(response_data)

    def put(self, request):
        if request.user.user_type != 'admin':
            return Response({'error': 'Only admins can access this endpoint'}, status=status.HTTP_403_FORBIDDEN)
        serializer = UserSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()

            # Invalidate cache
            cache_key = f'admin_profile_{request.user.id}'
            try:
                cache.delete(cache_key)
            except (InvalidCacheBackendError, Exception) as e:
                print(f"Failed to invalidate cache: {e}")

            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class GoogleAuthView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        id_token_str = request.data.get('id_token')
        if not id_token_str:
            logger.error('No ID token provided in Google auth request')
            return Response(
                {'error': 'No ID token provided'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            server_time = timezone.now()
            server_timestamp = int(time.time())
            logger.info(f'Server time: {server_time} (UTC timestamp: {server_timestamp})')

            # Verify the Google ID token with clock skew tolerance
            idinfo = id_token.verify_oauth2_token(
                id_token_str,
                Request(),
                settings.GOOGLE_CLIENT_ID,
                clock_skew_in_seconds=60  # Allow up to 60 seconds of clock skew
            )
            logger.info(f'Token info: {idinfo}')

            # Validate the token issuer
            if idinfo['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
                logger.error(f'Invalid token issuer: {idinfo["iss"]}')
                return Response(
                    {'error': 'Invalid token issuer'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            email = idinfo['email']
            name = idinfo.get('name', '')
            logger.info(f'Google token verified for email: {email}')

            # Get or create user
            try:
                user = User.objects.get(email=email)
                logger.info(f'Existing user found: {email}')
            except User.DoesNotExist:
                # Generate a unique username from email
                username = email.split('@')[0]
                counter = 1
                while User.objects.filter(username=username).exists():
                    username = f"{email.split('@')[0]}_{counter}"
                    counter += 1

                user = User.objects.create_user(
                    username=username,
                    email=email,
                    first_name=name.split()[0] if name else '',
                    last_name=' '.join(name.split()[1:]) if name and len(name.split()) > 1 else '',
                    user_type='customer',
                    is_verified=True
                )
                logger.info(f'Created new user: {email}')

            # Get or create token
            token, created = Token.objects.get_or_create(user=user)
            logger.info(f'Generated token for user: {email}, created: {created}')

            return Response({
                'message': 'Google login successful',
                'user_id': user.id,
                'username': user.username,
                'token': token.key
            }, status=status.HTTP_200_OK)

        except ValueError as e:
            logger.error(f'Invalid Google token: {str(e)}')
            return Response(
                {'error': f'Invalid Google token: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.error(f'Unexpected error during Google auth: {str(e)}', exc_info=True)
            return Response(
                {'error': 'Internal server error'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action == 'create':
            return RegisterSerializer
        elif self.action == 'update' or self.action == 'partial_update':
            return UserUpdateSerializer
        return super().get_serializer_class()

    def update(self, request, *args, **kwargs):
        instance = self.request.user
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        # Invalidate user profile and current user cache
        cache_key_profile = f'user_profile_{request.user.id}'
        cache_key_current = f'current_user_{request.user.id}'
        try:
            cache.delete(cache_key_profile)
            cache.delete(cache_key_current)
        except (InvalidCacheBackendError, Exception) as e:
            print(f"Failed to invalidate cache: {e}")

        return Response(serializer.data)


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            user = serializer.validated_data['user']

            # Check if user is verified
            if not user.is_verified:
                return Response({
                    'error': 'Please verify your email first',
                    'needs_verification': True,
                    'email': user.email
                }, status=status.HTTP_403_FORBIDDEN)

            token, created = Token.objects.get_or_create(user=user)
            return Response({
                'message': 'Login successful',
                'user_id': user.id,
                'username': user.username,
                'token': token.key
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request):
        if request.user.is_authenticated:
            return Response({
                'message': 'Logged in',
                'user_id': request.user.id,
                'username': request.user.username
            }, status=status.HTTP_200_OK)
        return Response({'message': 'Not logged in'}, status=status.HTTP_401_UNAUTHORIZED)


@api_view(['POST'])
def logout_view(request):
    try:
        if not request.user.is_authenticated:
            return JsonResponse({
                'status': 'error',
                'message': 'Authentication required'
            }, status=status.HTTP_401_UNAUTHORIZED)

        Token.objects.filter(user=request.user).delete()
        return JsonResponse({
            'status': 'success',
            'message': 'Successfully logged out'
        }, status=status.HTTP_200_OK)
    except Exception as e:
        print(f"Logout error: {str(e)}")
        return JsonResponse({
            'status': 'error',
            'message': 'An error occurred during logout'
        }, status=status.HTTP_400_BAD_REQUEST)


class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            # Create user but don't verify yet
            user = serializer.save()
            user.is_verified = False
            user.save()

            # Generate and send OTP
            otp = get_random_string(length=6, allowed_chars='0123456789')
            OTP.objects.filter(user=user).delete()  # Clear any existing OTPs
            OTP.objects.create(user=user, code=otp)

            # Send OTP email
            try:
                send_mail(
                    'Verify Your Account - OTP',
                    f'Your verification OTP is: {otp}\n\nThis OTP will expire in 10 minutes.',
                    'sales@mustardimports.co.ke',
                    [user.email],
                    fail_silently=False,
                )
            except Exception as e:
                print(f"Failed to send OTP email: {e}")
                user.delete()  # Remove user if email fails
                return Response({
                    'error': 'Failed to send verification email. Please try again.'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            return Response({
                'message': 'User registered successfully. Please check your email for OTP verification.',
                'user_id': user.id,
                'username': user.username,
                'email': user.email,
                'requires_otp': True
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        current_password = request.data.get('current_password')
        new_password = request.data.get('new_password')
        confirm_password = request.data.get('confirm_password')

        if not user.check_password(current_password):
            return Response({'error': 'Current password is incorrect'}, status=status.HTTP_400_BAD_REQUEST)

        if new_password != confirm_password:
            return Response({'error': 'New passwords do not match'}, status=status.HTTP_400_BAD_REQUEST)

        user.set_password(new_password)
        user.save()
        update_session_auth_hash(request, user)
        return Response({'message': 'Password changed successfully'}, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_current_user(request):
    cache_key = f'current_user_{request.user.id}'
    try:
        cached_data = cache.get(cache_key)
        if cached_data:
            return JsonResponse(cached_data)
    except (InvalidCacheBackendError, Exception) as e:
        print(f"Cache error: {e}. Falling back to direct query.")

    user = request.user
    response_data = {
        'id': user.id,
        'username': user.username,
    }

    try:
        cache.set(cache_key, response_data, timeout=60 * 5)  # Cache for 5 minutes
    except (InvalidCacheBackendError, Exception) as e:
        print(f"Failed to cache response: {e}")

    return JsonResponse(response_data)
