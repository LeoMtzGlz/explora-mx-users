# Register
from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.core.validators import validate_email
from django.core.exceptions import ValidationError as DjangoValidationError
from .utils import validate_phone_number
# Login
from django.contrib.auth import authenticate
# Logout
from rest_framework_simplejwt.tokens import RefreshToken, TokenError
# Generar OTP
from .models import PhoneOTP
from .utils import send_whatsapp_otp
import random


User = get_user_model()


class RegisterSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=True)
    phone_number = serializers.CharField(required=True)
    password = serializers.CharField(write_only=True, min_length=8)
    confirm_password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = ['username', 'email', 'phone_number', 'password', 'confirm_password']

    def validate_email(self, value):
        try:
            validate_email(value)
        except DjangoValidationError:
            raise serializers.ValidationError("Correo electrónico inválido.")
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Este correo ya está registrado.")
        return value

    def validate_phone_number(self, value):
        # Normaliza y valida usando tu función auxiliar
        formatted_phone = validate_phone_number(value)

        # Verifica si ya existe en formato normalizado
        if User.objects.filter(phone_number=formatted_phone).exists():
            raise serializers.ValidationError("Este número de teléfono ya está registrado.")

        return formatted_phone

    def validate(self, data):
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError({"password": "Las contraseñas no coinciden."})
        return data

    def create(self, validated_data):
        validated_data.pop('confirm_password')  # No lo necesitamos para crear al usuario
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            phone_number=validated_data['phone_number'],
            password=validated_data['password'],
        )
        return user

# Login serializer
class LoginSerializer(serializers.Serializer):
    identifier = serializers.CharField()  # Puede ser email, teléfono o username
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        identifier = data.get("identifier")
        password = data.get("password")

        user = authenticate(
            request=self.context.get('request'),
            username=identifier,
            password=password
        )

        if not user:
            raise serializers.ValidationError("Credenciales inválidas.")

        if not user.is_active:
            raise serializers.ValidationError("Usuario inactivo.")

        refresh = RefreshToken.for_user(user)
        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'user': {
                'id': user.id,
                'email': user.email,
                'username': user.username,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'phone_number': user.phone_number,
                'is_active': user.is_active
            }
        }

# Logout Serializer
class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField()

    def validate(self, attrs):
        self.token = attrs['refresh']
        return attrs

    def save(self, **kwargs):
        try:
            token = RefreshToken(self.token)
            token.blacklist()
        except TokenError:
            raise serializers.ValidationError("Token inválido o ya ha sido cerrado.")


# Serilizer para generar el OTP
class GenerateOTPSerializer(serializers.Serializer):
    phone_number = serializers.CharField()

    def validate_phone_number(self, value):
        print("Numero: " , value)
        user_exists = User.objects.filter(phone_number=value).exists()
        if not user_exists:
            raise serializers.ValidationError("El número no está registrado.")
        return value

    def create(self, validated_data):
        phone_number = validated_data['phone_number']
        otp = str(random.randint(100000, 999999))
        PhoneOTP.objects.update_or_create(phone_number=phone_number, defaults={'otp': otp})
        send_whatsapp_otp(phone_number, otp)
        return {"message": "Código enviado por WhatsApp"}


# Serializers para vreificar OTP
class VerifyOTPSerializer(serializers.Serializer):
    phone_number = serializers.CharField()
    otp = serializers.CharField()

    def validate(self, data):
        try:
            record = PhoneOTP.objects.get(phone_number=data['phone_number'], otp=data['otp'])
            if record.is_expired():
                raise serializers.ValidationError("El código ha expirado.")
        except PhoneOTP.DoesNotExist:
            raise serializers.ValidationError("Código inválido.")
        return data


# Establecer nueva contraseña
class ResetPasswordWithPhoneSerializer(serializers.Serializer):
    phone_number = serializers.CharField()
    otp = serializers.CharField()
    new_password = serializers.CharField(min_length=8)
    confirm_password = serializers.CharField(min_length=8)

    def validate(self, data):
        if data['new_password'] != data['confirm_password']:
            raise serializers.ValidationError("Las contraseñas no coinciden.")

        try:
            record = PhoneOTP.objects.get(phone_number=data['phone_number'], otp=data['otp'])
            if record.is_expired():
                raise serializers.ValidationError("El código ha expirado.")
        except PhoneOTP.DoesNotExist:
            raise serializers.ValidationError("Código inválido.")
        return data

    def save(self):
        user = User.objects.get(phone_number=self.validated_data['phone_number'])
        user.set_password(self.validated_data['new_password'])
        user.save()
        PhoneOTP.objects.filter(phone_number=self.validated_data['phone_number']).delete()
        return {"message": "Contraseña actualizada exitosamente."}
