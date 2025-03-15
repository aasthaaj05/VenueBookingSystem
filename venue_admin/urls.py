

from django.urls import path
from . import views



app_name = "venue_admin"  # This registers the namespace


urlpatterns = [
    
    path('home/', views.home, name='home'),
    path('requests/', views.get_requests, name='get_requests'),
    path('logout/', views.logout_view, name='logout'),

    path("approved-bookings/", views.approved_bookings_view, name="approved_bookings"),


]

