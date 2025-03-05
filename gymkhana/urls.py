from django.urls import path
# from .views import view_faculty_requests, venue_details , create_venue
from .views import approve_request, reject_request, cancel_request,pending_requests_by_date,create_venue, requests_for_gymkhana,request_booking,add_venue, decline_request

urlpatterns = [
    # path('requests/faculty/', view_faculty_requests, name='view_faculty_requests'),
    # path('venues/<uuid:venue_id>/', venue_details, name='venue_details'),
    path('create/', create_venue, name='create_venue'),
    path('request/<str:request_id>/approve/', approve_request, name='approve_request'),
    path('request/<str:request_id>/reject/', reject_request, name='reject_request'),
    path('request/<str:request_id>/cancel/', cancel_request, name='cancel_request'),
    path('requests/pending/', pending_requests_by_date, name='pending_requests_by_date'),
    # path('requests/gymkhana/', requests_for_gymkhana, name='requests_for_gymkhana'),
    path('requests/', requests_for_gymkhana, name='requests_for_gymkhana'),
    path('request_booking/', request_booking, name='request_booking'),
    path('approve/<str:request_id>/', approve_request, name='approve_request'),

    path('decline_request/<str:request_id>/' , decline_request , name="decline_request"),

    path("add_venue/", add_venue, name="add_venue"),
]

