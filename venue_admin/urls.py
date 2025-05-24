

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

]

