from django.urls import path
from . import views

urlpatterns = [
    path('send-otp/', views.send_otp_view, name='send-otp'),
    path('verify-otp/', views.verify_otp_view, name='verify-otp'),
    path('change-password/', views.change_password_view, name='change-password'),
]

