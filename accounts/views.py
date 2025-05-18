from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import (RegisterSerializer, LoginSerializer, LogoutSerializer,
                          GenerateOTPSerializer, VerifyOTPSerializer, ResetPasswordWithPhoneSerializer)
from django.contrib.auth import get_user_model

User = get_user_model()

class RegisterView(APIView):
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({'message': 'Usuario registrado exitosamente.'}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LoginView(APIView):
    def post(self, request):
        serializer = LoginSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            return Response(serializer.validated_data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LogoutView(APIView):
    def post(self, request):
        serializer = LogoutSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Sesión cerrada correctamente."}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Clase para Enviar el codigo
class SendOTPWhatsAppView(APIView):
    def post(self, request):
        serializer = GenerateOTPSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        result = serializer.save()
        return Response(result, status=status.HTTP_200_OK)

# Clase para verificar el codigo OTP
class VerifyOTPView(APIView):
    def post(self, request):
        serializer = VerifyOTPSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response({"message": "Código verificado."}, status=status.HTTP_200_OK)

# Clase para resetear el password
class ResetPasswordPhoneView(APIView):
    def post(self, request):
        serializer = ResetPasswordWithPhoneSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"message": "Contraseña restablecida con éxito."}, status=status.HTTP_200_OK)

"""
# ********************************************************
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
import logging

logger = logging.getLogger(__name__)

@api_view(['POST'])
def debug_logout(request):
    try:
        logger.debug("Logout request received: %s", request.data)
        refresh_token = request.data.get("refresh")
        token = RefreshToken(refresh_token)
        token.blacklist()
        logger.debug("Token blacklisted successfully.")
        return Response({"detail": "Logout exitoso."})
    except Exception as e:
        logger.exception("Error en logout:")
        return Response({"error": str(e)}, status=500)
"""