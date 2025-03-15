from django.db import models
from users.models import CustomUser  # Importing Users table
from gymkhana.models import Venue  # Importing Venue table
import uuid

class Request(models.Model):
    STATUS_CHOICES = [
        ('waiting_for_approval', 'Waiting for Approval'),  # Added new state
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('cancelled', 'Cancelled')
    ]   

    request_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="requests")  # Who made the request
    date = models.DateField()
    time = models.IntegerField()
    duration = models.IntegerField()  # Duration in minutes/hours
    venue = models.ForeignKey(Venue, on_delete=models.CASCADE, related_name="venue_requests")  # Requested Venue
    need = models.TextField(blank=True, null=True)  # Description of the need
    alternate_venue_1 = models.ForeignKey(Venue, on_delete=models.SET_NULL, null=True, related_name="alt_venue_1")  # First alternate venue
    alternate_venue_2 = models.ForeignKey(Venue, on_delete=models.SET_NULL, null=True, related_name="alt_venue_2")  # Second alternate venue
    event_details = models.TextField()  # Description of the event
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='waiting_for_approval')  # Default is waiting for approval
    reasons = models.CharField(max_length=255, blank=True, null=True)  # Reason for approval/rejection
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Request {self.request_id} by {self.user.name} for {self.venue.venue_name} ({self.status})"
