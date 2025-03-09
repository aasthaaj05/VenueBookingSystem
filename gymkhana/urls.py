from django.urls import path
from . import views

app_name = "gymkhana"

urlpatterns = [
    # path('requests/faculty/', view_faculty_requests, name='view_faculty_requests'),
    # path('venues/<uuid:venue_id>/', venue_details, name='venue_details'),
    path('create/', views.create_venue, name='create_venue'),
    path('request/<str:request_id>/approve/', views.approve_request, name='approve_request'),
    path('request/<str:request_id>/reject/', views.reject_request, name='reject_request'),
    path('request/<str:request_id>/cancel/', views.cancel_request, name='cancel_request'),
    path('requests/pending/', views.pending_requests_by_date, name='pending_requests_by_date'),
    path('requests/', views.requests_for_gymkhana, name='requests_for_gymkhana'),
    path('request_booking/', views.request_booking, name='request_booking'),
    path('approve/<str:request_id>/', views.approve_request, name='approve_request'),

    path('decline_request/<str:request_id>/' , views.decline_request , name="decline_request"),

    path("add_venue/", views.add_venue, name="add_venue"),

    path('dashboard/', views.gymkhana_dashboard, name='gymkhana_dashboard'),

    path('home/', views.home, name='home'),
    path('create_venue/', views.create_venue, name='create_venue'),

    
]

