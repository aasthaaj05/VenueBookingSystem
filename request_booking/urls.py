

from django.urls import path
from . import views
from .views import RequestMultipleWeekAvailabilityView


app_name = "request_booking"  # This registers the namespace


urlpatterns = [
    path('venues/', views.get_venues, name='get_venues'),
    path('venues/<str:venue_id>/', views.get_venue_details, name='get_venue_details'),  # ✅ Change int to uuid
    path('bookings/', views.get_available_slots, name='get_available_slots'),
    path('bookings/request/', views.request_slot, name='request_slot'),
    path('bookings/cancel/<str:request_id>', views.cancel_request, name='cancel_request'),
    path('user/requests/', views.get_user_requests, name='get_user_requests'),
    path('calendar/', views.get_available_slots, name='get_available_slots'),
    path('book/', views.book_venue, name='book_venue'),
    # path('user_dashboard/', views.venue_list, name='user_dashboard'),  
    path('user_dashboard/<str:building_name>/', views.user_dashboard, name='user_dashboard'),

    # path('request_multiple/', views.process_booking_multiple, name="request_multiple_week_availability_view"),

    path(
        'request_multiple/',
        RequestMultipleWeekAvailabilityView.as_view(),
        name='request_multiple_week_availability_view'
    ),


    path("book_venue/", views.book_venue, name="book_venue"),
    path("process_booking/", views.process_booking, name="process_booking"),
    
    path("booking_status/", views.booking_status, name="booking_status"),
    path("getUnavailableSlots/", views.getUnavailableSlots, name="get_unavailable_slots"),
    path('buildings/', views.get_buildings, name='get_buildings'),
    path('home/', views.index, name='index'),
    path('cancel-booking/', views.cancel_booking, name='cancel_booking'),
]
  




