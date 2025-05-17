
from django.contrib.auth.models import AbstractUser
from django.db import models

from django.utils import timezone
from datetime import timedelta

class CustomUser(AbstractUser):
    phone_number = models.CharField(max_length=20, unique=True, null=True, blank=True)

    def __str__(self):
        return self.username

    class Meta:
        verbose_name = "CustomUser"
        verbose_name_plural = "CustomUsers"

# Crear el Modelo PhoneOTP
class PhoneOTP(models.Model):
    phone_number = models.CharField(max_length=20, unique=True)
    otp = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)

    def is_expired(self):
        return timezone.now() > self.created_at + timedelta(minutes=10)

    def __str__(self):
        return f'{self.phone_number} - {self.otp}'