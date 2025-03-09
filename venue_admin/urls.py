

from django.urls import path
from . import views



app_name = "venue_admin"  # This registers the namespace


urlpatterns = [
    
    path('home/', views.home, name='home'),
    path('requests/', views.get_requests, name='get_requests'),
]

