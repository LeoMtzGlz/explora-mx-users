
from django.urls import path
from .views import (RegisterView, LoginView, LogoutView,
                    SendOTPWhatsAppView, VerifyOTPView, ResetPasswordPhoneView

                    )

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
]

# URLs para enviar código por WhatsApp
urlpatterns += [
    path('send_otp/', SendOTPWhatsAppView.as_view(), name='send_otp'),
    path('verify_otp/', VerifyOTPView.as_view(), name='verify_otp'),
    path('reset_password_phone/', ResetPasswordPhoneView.as_view(), name='reset_password_phone'),
]