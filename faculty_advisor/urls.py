




from django.urls import path
# from .views import view_faculty_requests, venue_details , create_venue
from . import views
urlpatterns = [
    path("forward_requests/", views.get_pending_forward_requests, name="get_pending_forward_requests"),
    path("forward_requests/<str:req_id>/accept", views.accept_pending_forward_requests, name="accept_pending_forward_requests"),
    path("forward_requests/<str:req_id>/decline", views.decline_pending_forward_requests, name="decline_pending_forward_requests"),

]

