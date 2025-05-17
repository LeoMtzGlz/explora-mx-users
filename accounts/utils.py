import phonenumbers
from rest_framework import serializers
from twilio.rest import Client
import os
from decouple import config


def validate_phone_number(value):
    try:
        # Intenta parsear el número con el país por defecto (ejemplo: México = "MX")
        phone_obj = phonenumbers.parse(value, config('DEFAULT_COUNTRY') )

        # Verifica si es válido
        if not phonenumbers.is_valid_number(phone_obj):
            raise serializers.ValidationError("Número de teléfono inválido.")

        # Devuelve el número en formato internacional estándar (E.164)
        return phonenumbers.format_number(phone_obj, phonenumbers.PhoneNumberFormat.E164)

    except phonenumbers.NumberParseException:
        raise serializers.ValidationError("Formato de número de teléfono incorrecto. Asegúrate de incluir el código de país (+52 para MX, +1 para US).")



def send_whatsapp_otp(phone_number, otp):
    client = Client(config('TWILIO_ACCOUNT_SID'), config('TWILIO_AUTH_TOKEN') )
    message = client.messages.create(
                                    from_=f"whatsapp:{config('TWILIO_WHATSAPP_NUMBER') }",  # Número oficial de Twilio para WhatsApp
                                    body=f"Tu código de verificación es: {otp}",
                                    to=f"whatsapp:{phone_number}"
                                )
    print(f"Mensaje enviado con SID: {message.sid}, Status: {message.status}")
    return message.sid
