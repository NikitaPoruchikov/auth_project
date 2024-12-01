import random
import time
import string

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.authtoken.models import Token
from django.contrib.auth import get_user_model

from .models import User
from .serializers import UserSerializer
from .constants import generate_username, AUTH_CODE_LENGTH, INVAITE_CODE_LENGTH


class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        phone_number = request.data.get('phone_number')
        password = request.data.get('password')
        username = request.data.get('username')

        # Создание нового пользователя
        user = get_user_model().objects.create_user(
            phone_number=phone_number,
            password=password,
            # Случайное имя, если не передано
            username=generate_username(username),
        )

        return Response({"message": "User registered successfully"},
                        status=status.HTTP_201_CREATED)


class SendCodeView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        phone_number = request.data.get('phone_number')
        if not phone_number:
            return Response({'detail': 'Phone number is required'},
                            status=status.HTTP_400_BAD_REQUEST)

        # Ищем пользователя с таким номером телефона
        try:
            user = User.objects.get(phone_number=phone_number)
        except User.DoesNotExist:
            return Response({'detail': 'User not found'},
                            status=status.HTTP_404_NOT_FOUND)

        # Генерация 4-значного кода
        auth_code = ''.join(random.choices('0123456789', k=AUTH_CODE_LENGTH))
        user.auth_code = auth_code
        user.save()

        # Имитация задержки перед отправкой кода
        time.sleep(random.uniform(1, 2))
        return Response({'auth_code': auth_code},
                        status=status.HTTP_200_OK)


class VerifyCodeView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        phone_number = request.data.get('phone_number')
        auth_code = request.data.get('auth_code')

        if not phone_number or not auth_code:
            return Response({'detail': 'Phone number and code are required'},
                            status=status.HTTP_400_BAD_REQUEST)

        # Проверяем, существует ли пользователь с таким номером телефона
        user = User.objects.filter(phone_number=phone_number).first()

        if user:
            # Проверка правильности кода
            if user.auth_code == auth_code:
                # Если код правильный, создаем простой токен
                token, created = Token.objects.get_or_create(user=user)

                return Response({
                    "message": "Verification successful",
                    "token": token.key  # Возвращаем токен
                }, status=status.HTTP_200_OK)
            else:
                return Response({'detail': 'Invalid auth code'},
                                status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'detail': 'User not found'},
                            status=status.HTTP_404_NOT_FOUND)


class LoginView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # Получаем пользователя из запроса
        user = request.user

        if user:
            if user.activated_invite_code:
                return Response({
                    "detail": "Invite code already activated",
                    "activated_invite_code": user.activated_invite_code
                }, status=status.HTTP_400_BAD_REQUEST)

            if not user.invite_code:
                invite_code = ''.join(random.choices(
                    string.ascii_uppercase + string.digits,
                    k=INVAITE_CODE_LENGTH))
                user.invite_code = invite_code
                user.save()

                return Response({
                    "message": "Invite code generated",
                    "invite_code": invite_code
                }, status=status.HTTP_200_OK)
            else:
                return Response({
                    "detail": "Invite code already exists"
                }, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({
                "detail": "User not found"
            }, status=status.HTTP_404_NOT_FOUND)


class ProfileView(APIView):
    # Убедитесь, что тут будет правильная настройка прав доступа
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        # Если пользователь не аутентифицирован, возвращаем ошибку
        if not user.is_authenticated:
            return Response({'detail':
                             'Authentication credentials were not provided.'},
                            status=status.HTTP_401_UNAUTHORIZED)

        referrals = User.objects.filter(referred_by=user)
        referrals_phone_numbers = [
            referral.phone_number for referral in referrals]

        # Проверяем, активировал ли пользователь инвайт-код
        activated_invite_code = (
            user.activated_invite_code if user.activated_invite_code else None)

        # Сериализуем данные пользователя
        serializer = UserSerializer(user)

        return Response({
            'user': serializer.data,
            'referrals': referrals_phone_numbers,
            'activated_invite_code': activated_invite_code
        })


class ActivateInviteView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        phone_number = request.data.get('phone_number')
        invite_code = request.data.get('invite_code')

        # Получаем пользователя
        user = User.objects.filter(phone_number=phone_number).first()

        if not user:
            return Response({'detail': 'User not found'},
                            status=status.HTTP_404_NOT_FOUND)

        # Проверяем, существует ли инвайт-код
        referrer = User.objects.filter(invite_code=invite_code).first()

        if not referrer:
            return Response({'detail': 'Invalid invite code'},
                            status=status.HTTP_400_BAD_REQUEST)

        # Проверяем, не активировал ли уже пользователь инвайт-код
        if user.activated_invite_code:
            return Response({'detail': 'You have invite code'},
                            status=status.HTTP_400_BAD_REQUEST)

        # Активируем инвайт-код
        user.activated_invite_code = invite_code
        user.referred_by = referrer
        user.save()

        return Response({
            "message": "Invite code activated successfully",
            "activated_invite_code": invite_code
        }, status=status.HTTP_200_OK)
