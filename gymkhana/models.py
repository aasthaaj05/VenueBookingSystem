from django.db import models

import uuid

# Create your models here.


from django.db import models
from users.models import CustomUser  # Importing Users table

class Venue(models.Model):
    id = models.UUIDField(primary_key=True,default=uuid.uuid4, editable=False)
    venue_name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True, null=True)
    photo_url = models.TextField(blank=True, null=True)  # Store image URLs
    capacity = models.IntegerField()
    address = models.TextField()
    facilities = models.JSONField(default=list)  # Store facilities as JSON array
    department_incharge = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, related_name="managed_venues")  # FK to Users

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.venue_name
    


from django.db import models
from users.models import CustomUser  # Import User model
from gymkhana.models import Venue  # Import Venue model
from request_booking.models import Request  # Import Venue model

import uuid

class Booking(models.Model):
    booking_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    request = models.OneToOneField(Request, on_delete=models.CASCADE, related_name="booking")  # Link to the original request
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="bookings")  # Who made the booking
    date = models.DateField()
    time = models.IntegerField()
    duration = models.IntegerField()
    venue = models.ForeignKey(Venue, on_delete=models.CASCADE, related_name="booked_venue")  # Final booked venue
    event_details = models.TextField()  # Description of the event
    msg = models.TextField(blank=True, null=True)  # Additional messages
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Booking {self.booking_id} by {self.user} for {self.venue} on {self.date}"
    

    

from django.db import models
import uuid




class RejectedBooking(models.Model):
    rejection_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    request = models.OneToOneField(
        Request, 
        on_delete=models.CASCADE, 
        related_name="rejected_request"  # ✅ Unique related_name to avoid conflict
    )  
    user = models.ForeignKey(
        CustomUser, 
        on_delete=models.CASCADE, 
        related_name="rejected_requests"  # ✅ Unique related_name
    )  
    date = models.DateField()
    time = models.IntegerField()
    duration = models.IntegerField()
    
    venue = models.ForeignKey(
        Venue, 
        on_delete=models.CASCADE, 
        related_name="rejected_venues"  # ✅ Unique related_name
    )  
    
    event_details = models.TextField()
    rejection_reason = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Rejected Booking {self.rejection_id} by {self.user} for {self.venue} on {self.date}"


    



from django.db import models
from users.models import CustomUser
from gymkhana.models import Venue
import uuid


class Rejection(models.Model):
    rejection_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    request = models.OneToOneField(Request, on_delete=models.CASCADE, related_name="rejection")
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="rejections")
    reason = models.TextField()
    msg = models.TextField(blank=True, null=True)  # Additional rejection message
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Rejection {self.rejection_id} for Request {self.request.request_id}"






