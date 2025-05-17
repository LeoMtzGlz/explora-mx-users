from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model

User = get_user_model()

class EmailOrPhoneBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        user = None

        # Permitir login con email, teléfono o username
        identifier = kwargs.get('email') or kwargs.get('phone_number') or username

        try:
            if '@' in identifier:
                user = User.objects.get(email=identifier)
            elif identifier.startswith('+') or identifier.isdigit():
                user = User.objects.get(phone_number=identifier)
            else:
                user = User.objects.get(username=identifier)
        except User.DoesNotExist:
            return None

        if user and user.check_password(password):
            return user
        return None

"""
class EmailBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        email = kwargs.get('email', username)
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return None
        if user.check_password(password):
            return user
        return None
"""