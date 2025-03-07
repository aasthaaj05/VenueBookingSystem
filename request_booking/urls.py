

from django.urls import path
from . import views

urlpatterns = [
    path('venues/', views.get_venues, name='get_venues'),
    path('venues/<str:venue_id>/', views.get_venue_details, name='get_venue_details'),  # ✅ Change int to uuid
    path('bookings/', views.get_available_slots, name='get_available_slots'),
    path('bookings/request/', views.request_slot, name='request_slot'),
    path('bookings/cancel/', views.cancel_request, name='cancel_request'),
    path('user/requests/', views.get_user_requests, name='get_user_requests'),
    path('calendar/', views.get_available_slots, name='get_available_slots'),
    path('book/', views.book_venue, name='book_venue'),
    path('user_dashboard/', views.venue_list, name='user_dashboard'),  

    path("book_venue/", views.book_venue, name="book_venue"),
    path("process_booking/", views.process_booking, name="process_booking"),
    
    path("booking_status/", views.booking_status, name="booking_status"),
    path("getUnavailableSlots/", views.getUnavailableSlots, name="get_unavailable_slots")
]
  




