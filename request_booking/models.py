from django.db import models
from users.models import CustomUser  # Importing Users table
from gymkhana.models import Venue  # Importing Venue table
import uuid

# class Request(models.Model):
#     STATUS_CHOICES = [
#         ('waiting_for_approval', 'Waiting for Approval'),  # Added new state
#         ('pending', 'Pending'),
#         ('approved', 'Approved'),
#         ('rejected', 'Rejected'),
#         ('cancelled', 'Cancelled'),
#         ('forwarded', 'Forwarded')
#     ]   

#     request_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
#     user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="requests")  # Who made the request
#     date = models.DateField()
#     time = models.IntegerField()
#     duration = models.IntegerField()  # Duration in minutes/hours
#     venue = models.ForeignKey(Venue, on_delete=models.CASCADE, related_name="venue_requests")  # Requested Venue
#     need = models.TextField(blank=True, null=True)  # Description of the need
#     alternate_venue_1 = models.ForeignKey(Venue, on_delete=models.SET_NULL, null=True, related_name="alt_venue_1")  # First alternate venue
#     alternate_venue_2 = models.ForeignKey(Venue, on_delete=models.SET_NULL, null=True, related_name="alt_venue_2")  # Second alternate venue
#     event_details = models.TextField()  # Description of the event
#     status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='waiting_for_approval')  # Default is waiting for approval
#     reasons = models.CharField(max_length=255, blank=True, null=True)  # Reason for approval/rejection
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)

#     def __str__(self):
#         return f"Request {self.request_id} by {self.user.name} for {self.venue.venue_name} ({self.status})"

import uuid
from django.db import models
from django.contrib.auth import get_user_model

CustomUser = get_user_model()

class Request(models.Model):
    STATUS_CHOICES = [
        ('waiting_for_approval', 'Waiting for Approval'),  # Default state
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('cancelled', 'Cancelled'),
        ('forwarded', 'Forwarded'),
        ('user-cancelled', 'User-Cancelled')
    ]   

    request_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="requests")  # Who made the request
    # email = models.EmailField(max_length=255)  # User's email
    email = models.EmailField(max_length=255, blank=True, null=True)

    # phone_number = models.CharField(max_length=15)  # Contact number
    phone_number = models.CharField(max_length=15, blank=True, null=True)

    full_name = models.CharField(max_length=255, blank=True, null=True)  # New field
    organization_name = models.CharField(max_length=255, blank=True, null=True)  # New field

    event_details = models.TextField(blank=True, null=True)  # Updated: made optional
    purpose = models.TextField(blank=True, null=True)  # New field

    
    # event_type = models.CharField(max_length=100)  # Type of event
    
    event_type = models.CharField(max_length=255, blank=True, null=True)

    guest_count = models.IntegerField(default=0)  # New field

    additional_info = models.TextField(blank=True, null=True)  # Additional details

    date = models.DateField()
    time = models.IntegerField()  # Changed from IntegerField to TimeField
    duration = models.IntegerField()  # Duration in minutes/hours

    venue = models.ForeignKey(Venue, on_delete=models.CASCADE, related_name="venue_requests")  # Requested Venue
    need = models.TextField(blank=True, null=True)  # Description of the need
    alternate_venue_1 = models.ForeignKey(Venue, on_delete=models.SET_NULL, null=True, related_name="alt_venue_1")  # First alternate venue
    alternate_venue_2 = models.ForeignKey(Venue, on_delete=models.SET_NULL, null=True, related_name="alt_venue_2")  # Second alternate venue
    event_details = models.TextField()  # Description of the event

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='waiting_for_approval')  # Default status
    reasons = models.CharField(max_length=255, blank=True, null=True)  # Reason for approval/rejection

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Request {self.request_id} by {self.user.name} for {self.venue.venue_name} ({self.status})"

