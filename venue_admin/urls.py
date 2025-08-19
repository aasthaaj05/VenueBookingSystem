

from django.urls import path
from . import views



app_name = "venue_admin"  # This registers the namespace


urlpatterns = [
    
    path('home/', views.home, name='home'),
    path('requests/', views.request_booking, name='get_requests'),
    path('cumulative_requests/', views.cumulative_request_booking, name='get_cumulative_requests'),
    path('logout/', views.logout_view, name='logout'),
    path('reject_request/<uuid:request_id>', views.reject_request, name='reject_request'),
    path("approved-bookings/", views.approved_bookings_view, name="approved_bookings"),

    
    path("cumulative-approved-bookings/", views.approved_cumulative_bookings_view, name="approved_cumulative_bookings_view"),
    path("rejected-approved-bookings/", views.rejected_cumulative_bookings_view, name="rejected_cumulative_bookings_view"),

    path('cancel-cumulative-booking/<uuid:cumulative_request_id>/', views.cumulative_cancel_booking, name='cumulative_cancel_booking'),



    path('approve_request/<uuid:request_id>', views.approve_request, name="approve_request"),
    
    path(
        'approve_cumulative_request/<uuid:cumulative_request_id>',
        views.approve_cumulative_request,
        name='approve_cumulative_request'
    ),
    path(
        'reject_cumulative_request/<uuid:cumulative_request_id>',
        views.reject_cumulative_request,
        name='reject_cumulative_request'
    ),

    path('venues/edit/', views.venue_edit_start, name='venue_edit_start'),
    path('venues/edit/<uuid:venue_id>/', views.venue_edit_form, name='venue_edit_form'),

    path('users/', views.user_list, name='user_list'),
    path('users/<uuid:user_id>/', views.user_detail, name='user_detail'),
    path('users/add/', views.add_user, name='add_user'),
    path('users/delete/<uuid:user_id>/', views.delete_user, name='delete_user'),

    path('venues/create/', views.venue_create, name='venue_create'),

    path('venue/delete/<uuid:pk>/', views.venue_delete, name='venue_delete'),

    path('venue-schedule/', views.VenueListView.as_view(), name='venue_schedule'),
    # path('api/bookings/', views.BookingScheduleAPI.as_view(), name='booking_schedule_api'),
    path('bookings/schedule/', views.BookingScheduleAPI.as_view(), name='booking-schedule-api'),


]

