from django.urls import path
from . import views

app_name = "users"  # This registers the namespace


urlpatterns = [
    path('register/', views.register_view, name='register'),  # Signup
    path('login/', views.login_view, name='login'),  # Login
    path('home/', views.home, name='home'),  # Get all users
    path('calendar/', views.calendar_view, name='calendar'),
    # path('submit_booking/', views.submit_booking, name='submit_booking'),
    path('clear-and-forgot/', views.clear_flash_and_redirect, name='clear_and_forgot'),

    path('venue-schedule/', views.VenueListView.as_view(), name='venue_schedule'),
    # path('api/bookings/', views.BookingScheduleAPI.as_view(), name='booking_schedule_api'),
    path('bookings/schedule/', views.BookingScheduleAPI.as_view(), name='booking-schedule-api'),


]

