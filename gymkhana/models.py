from django.db import models

import uuid

# Create your models here.


from django.db import models
from users.models import CustomUser  # Importing Users table

# class Venue(models.Model):
#     id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
#     venue_name = models.CharField(max_length=255, unique=True)
#     description = models.TextField(blank=True, null=True)
#     photo_url = models.TextField(blank=True, null=True)  # Store image URLs
#     capacity = models.IntegerField()
#     address = models.TextField()
#     facilities = models.JSONField(default=list)  # Store facilities as JSON array
#     department_incharge = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, related_name="managed_venues")  # FK to Users
#     building_name = models.CharField(max_length=255, blank=True, null=True)  # New field
#     floor_number = models.IntegerField(blank=True, null=True)  # New field
#     room_number = models.CharField(max_length=50, blank=True, null=True)  # New field
    
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)

#     def __str__(self):
#         return self.venue_name


import uuid
from django.db import models
from users.models import CustomUser  # Importing Users table

from django.db import models

class Building(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, unique=True)  # Unique building name
    location = models.TextField()  # Address or location details
    total_floors = models.IntegerField(blank=True, null=True)  # Number of floors
    photo_url = models.TextField(blank=True, null=True)  # Store image URLs
    description = models.TextField(blank=True, null=True)  # Additional details

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name




# Update the Venue model to use a ForeignKey to Building

class Venue(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    venue_name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True, null=True)
    photo_url = models.TextField(blank=True, null=True)  # Store image URLs
    capacity = models.IntegerField(null=True)
    address = models.TextField(null=True)
    facilities = models.JSONField(default=list)  # Store facilities as JSON array
    department_incharge = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, related_name="managed_venues")
    
    building = models.ForeignKey(Building, on_delete=models.CASCADE, related_name="venues", null=True, blank=True)
    floor_number = models.TextField(blank=True, null=True)
    room_number = models.CharField(max_length=50, blank=True, null=True)

    # New fields from the table
    class_type = models.CharField(max_length=100, blank=True, null=True, help_text="Class Room / Lab / Seminar Hall")
    class_number = models.CharField(max_length=100, blank=True, null=True, help_text="Class Room No / Lab No / Seminar Hall No")
    length = models.FloatField(blank=True, null=True)
    depth_or_height = models.FloatField(blank=True, null=True, help_text="D/h")
    area_sqm = models.FloatField(blank=True, null=True)
    picture_urls = models.TextField(blank=True, null=True)  # If different from photo_url
    usage_type = models.CharField(max_length=255, blank=True, null=True, help_text="Hands-on session, lecture, lab, etc.")
    venue_location = models.TextField(blank=True, null=True)
    
    dept_incharge_phone = models.CharField(max_length=20, blank=True, null=True)
    dept_incharge_email = models.EmailField(blank=True, null=True)
    dept_assistant_name1 = models.CharField(max_length=255, blank=True, null=True)
    dept_assistant_name2 = models.CharField(max_length=255, blank=True, null=True)
    
    campus = models.CharField(max_length=20, choices=[('North', 'North'), ('South', 'South')], blank=True, null=True)

    venue_admin = models.EmailField(blank=True, null=True)

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
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('cancelled', 'Cancelled'),
        ('user-cancelled','User-cancelled')
    ]

    booking_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    request = models.OneToOneField(Request, on_delete=models.CASCADE, related_name="booking")  # Link to the original request
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="bookings")  # Who made the booking
    date = models.DateField()
    time = models.CharField(max_length=100)
    duration = models.CharField(max_length=100)
    venue = models.ForeignKey(Venue, on_delete=models.CASCADE, related_name="booked_venue")  # Final booked venue
    # event_details = models.TextField(null=True, default="Details not Provided")  # Description of the event
    event_details = models.TextField(null=True, blank=True)
    msg = models.TextField(blank=True, null=True)  # Additional messages
    status = models.CharField(max_length=100, choices=STATUS_CHOICES, default="active")  # Booking status
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    additional_comments_Venueadmin = models.CharField(max_length=1000, default="active")  # Booking status
    reason_for_approval = models.CharField(max_length=1000, default="active")  # Booking status


    def __str__(self):
        return f"Booking {self.booking_id} by {self.user} for {self.venue} on {self.date} ({self.status})"


    

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
    time = models.CharField(max_length=100)
    duration = models.CharField(max_length=100)
    
    venue = models.ForeignKey(
        Venue, 
        on_delete=models.CASCADE, 
        related_name="rejected_venues"  # ✅ Unique related_name
    )  
    
    event_details = models.TextField()
    rejection_reason = models.TextField()
    feedback_from_admin = models.CharField(max_length=1000, blank=True, null=True)  # ✅ New field
    alternate_venues_suggestion = models.CharField(max_length=1000, blank=True, null=True)  # ✅ New field
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
    feedback_from_admin = models.CharField(max_length=1000, blank=True, null=True)  # ✅ New field
    alternate_venues_suggestion = models.CharField(max_length=1000, blank=True, null=True)  # ✅ New field

    def __str__(self):
        return f"Rejection {self.rejection_id} for Request {self.request.request_id}"






