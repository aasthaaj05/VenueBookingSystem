

from django.urls import path
from . import views
urlpatterns = [
    path("forward_requests/", views.get_pending_forward_requests, name="get_pending_forward_requests"),
    path("forward_requests/<str:req_id>/accept", views.accept_pending_forward_requests, name="accept_pending_forward_requests"),
    path("forward_requests/<str:req_id>/decline", views.decline_pending_forward_requests, name="decline_pending_forward_requests"),

    path("faculty_advisor_dashboard/", views.faculty_advisor_dashboard, name="faculty_advisor_dashboard"),

]

