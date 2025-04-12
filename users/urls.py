from django.urls import path
from . import views

app_name = "users"  # This registers the namespace


urlpatterns = [
    path('register/', views.register_view, name='register'),  # Signup
    path('login/', views.login_view, name='login'),  # Login
    path('home/', views.home, name='home'),  # Get all users
    path('calendar/', views.calendar_view, name='calendar'),
    # path('submit_booking/', views.submit_booking, name='submit_booking'),
]

