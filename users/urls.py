from django.urls import path
from .views import register_view, login_view, home,calendar_view, submit_booking

urlpatterns = [
    path('register/', register_view, name='register'),  # Signup
    path('login/', login_view, name='login'),  # Login
    path('home/', home, name='home'),  # Get all users
    path('calendar/', calendar_view, name='calendar'),
    path('submit_booking/', submit_booking, name='submit_booking'),
]

