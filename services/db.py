# from django.db import connection

# # def getVenuesFromDB(limit):
# #     query = """
# #                 SELECT venue_name, facilities, photo_url
# #                 FROM gymkhana_venue
# #                 LIMIT %s
# #             """
# #     with connection.cursor() as cursor:
# #         cursor.execute(query, (limit, ))
# #         result=cursor.fetchall()

# #     return result

# from django.db import connection

# def getVenuesFromDB(limit):
#     query = """
#                 SELECT venue_name, facilities, photo_url
#                 FROM gymkhana_venue
#                 LIMIT %s
#             """
#     with connection.cursor() as cursor:
#         cursor.execute(query, (limit,))
#         columns = [col[0] for col in cursor.description]  # ✅ Get column names
#         result = [dict(zip(columns, row)) for row in cursor.fetchall()]  # ✅ Convert to list of dicts

#     return result  # ✅ Returns JSON-like list of dictionaries


# def getVenueDetailsFromDB(venue_id):
#     query = """
#                 SELECT *
#                 FROM gymkhana_venue
#                 WHERE gymkhana_venue.id=%s
#             """
#     with connection.cursor() as cursor:
#         cursor.execute(query, (venue_id, ))
#         result=cursor.fetchall()

#     return result

# def getUserRequestsFromDB(user_id):
#     query = """
#                 SELECT r.request_id, r.date, r.time, r.duration, r.status, v.venue_name
#                 FROM request_booking_request r 
#                 JOIN gymkhana_venue v ON r.venue_id = v.id
#                 WHERE r.user_id=%s;
#             """
#     with connection.cursor() as cursor:
#         cursor.execute(query, (user_id, ))
#         result=cursor.fetchall()

#     return result

# def requestSlotFromDB(venue_id, user_id, date, time, duration, alternate_venues, event_details, need):
#     query = """
#             INSERT INTO request_booking_request(venue_id, user_id, date, time, duration, alternate_venue_1, alternate_venue_2, event_details, need)
#             VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s);
#             """
#     with connection.cursor() as cursor:
#         cursor.execute(query, (venue_id, user_id, date, time, duration, alternate_venues[0], alternate_venues[1], event_details, need))
#         connection.commit()
#     return True

# def getBookedSlotsFromDB(venue_id, start_date, end_date):
#     query = """
#             SELECT r.date, r.time, r.duration
#             FROM gymkhana_booking r
#             WHERE (r.venue_id = %s) AND (r.date BETWEEN %s AND %s);
#             """
#     with connection.cursor() as cursor:
#         cursor.execute(query, (venue_id, start_date, end_date))
#         res=cursor.fetchall()
#     return res

# def cancelRequestFromDB(req_id):
#     query = """
#             DELETE
#             FROM request_booking_request
#             WHERE request_booking_request.request_id=%s
#             """
#     with connection.cursor() as cursor:
#         cursor.execute(query, (req_id, ))
#         connection.commit()
#     return True


from django.db import connection
import uuid



# ✅ Get venue details as JSON
def getVenueDetailsFromDB(venue_id):
    query = """
                SELECT *
                FROM gymkhana_venue
                WHERE gymkhana_venue.id=%s
            """
    with connection.cursor() as cursor:
        cursor.execute(query, (venue_id,))
        columns = [col[0] for col in cursor.description]  # ✅ Get column names
        result = [dict(zip(columns, row)) for row in cursor.fetchall()]  # ✅ Convert to list of dicts

    return result  # ✅ Returns JSON-like list of dictionaries

# ✅ Get user requests as JSON
def getUserRequestsFromDB(user_id):
    query = """
                SELECT r.request_id, r.date, r.time, r.duration, r.status, v.venue_name
                FROM request_booking_request r 
                JOIN gymkhana_venue v ON r.venue_id = v.id
                WHERE r.user_id=%s;
            """
    with connection.cursor() as cursor:
        cursor.execute(query, (user_id,))
        columns = [col[0] for col in cursor.description]  # ✅ Get column names
        result = [dict(zip(columns, row)) for row in cursor.fetchall()]  # ✅ Convert to list of dicts

    return result  # ✅ Returns JSON-like list of dictionaries

# ✅ Get booked slots as JSON
def getBookedSlotsFromDB(venue_id, start_date, end_date):
    query = """
            SELECT r.date, r.time, r.duration
            FROM gymkhana_booking r
            WHERE (r.venue_id = %s) AND (r.date BETWEEN %s AND %s);
            """
    with connection.cursor() as cursor:
        cursor.execute(query, (venue_id, start_date, end_date))
        columns = [col[0] for col in cursor.description]  # ✅ Get column names
        result = [dict(zip(columns, row)) for row in cursor.fetchall()]  # ✅ Convert to list of dicts

    return result  # ✅ Returns JSON-like list of dictionaries

# # ✅ Insert slot request (No changes needed)
# def requestSlotFromDB(venue_id, user_id, date, time, duration, alternate_venues, event_details, need):

#     # Generate UUID for request_id if not set
#     request_id = str(uuid.uuid4())  # Generate UUID

#     query = """
#             INSERT INTO request_booking_request(request_id , venue_id, user_id, date, time, duration, alternate_venue_1_id, alternate_venue_2_id, event_details, need)
#             VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
#             """
#     with connection.cursor() as cursor:
#         cursor.execute(query, (venue_id, user_id, date, time, duration, alternate_venues[0], alternate_venues[1], event_details, need))
#         connection.commit()
#     return True


import uuid

# def requestSlotFromDB(venue_id, user_id, date, time, duration, alternate_venues, event_details, need):
#     # Generate UUID for request_id
#     # request_id = uuid.uuid4()  # Generate UUID
#     # Generate UUID for request_id and remove hyphens
#     request_id = str(uuid.uuid4()).replace("-", "")  # Remove hyphens
    
#     print(request_id)

#     query = """
#             INSERT INTO request_booking_request(request_id , venue_id, user_id, date, time, duration, alternate_venue_1_id, alternate_venue_2_id, event_details,status, need)
#             VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s,'pending' ,%s);
#             """
#     with connection.cursor() as cursor:
#         cursor.execute(query, (
#             request_id,  # Pass the generated UUID as the first argument
#             venue_id, user_id, date, time, duration,
#             alternate_venues[0] if len(alternate_venues) > 0 else None,
#             alternate_venues[1] if len(alternate_venues) > 1 else None,
#             event_details,need
#         ))
#         connection.commit()
#     return True

# def requestSlotFromDB(venue_id, user_id, date, time, duration, alternate_venues, event_details, need):
#     # Generate UUID for request_id and remove hyphens
#     request_id = str(uuid.uuid4()).replace("-", "")  # Remove hyphens
    
#     print(request_id)

#     # Removed 'created_at' from the query since Django will handle it with auto_now_add=True
#     query = """
#             INSERT INTO request_booking_request(request_id , venue_id, user_id, date, time, duration, alternate_venue_1_id, alternate_venue_2_id, event_details, status, need)
#             VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, 'pending', %s);
#             """
#     with connection.cursor() as cursor:
#         cursor.execute(query, (
#             request_id,  # Pass the generated UUID as the first argument
#             venue_id, user_id, date, time, duration,
#             alternate_venues[0] if len(alternate_venues) > 0 else None,
#             alternate_venues[1] if len(alternate_venues) > 1 else None,
#             event_details, need
#         ))
#         connection.commit()
#     return True

from request_booking.models import Venue, Request
from gymkhana.models import Booking

def getVenuesFromDB(limit):
    return list(Venue.objects.all()[:limit].values('venue_name', 'facilities', 'photo_url'))

def getVenueDetailsFromDB(venue_id):
    venue = Venue.objects.filter(id=venue_id).values().first()
    return venue if venue else None

def getUserRequestsFromDB(user_id):
    return list(Request.objects.filter(user_id=user_id).values('id', 'date', 'time', 'duration', 'status', 'venue__venue_name'))

# def requestSlotFromDB(venue_id, user_id, date, time, duration, alternate_venues, event_details, need):
#     try:
#         venue = Venue.objects.get(id=venue_id)
#         print('chsihoiushos')
#         alternate_venue_1 = Venue.objects.get(id=alternate_venues[0]) if alternate_venues[0] else None
#         print('lilbli;')
#         alternate_venue_2 = Venue.objects.get(id=alternate_venues[1]) if alternate_venues[1] else None

#         print('alternate_venue_1 : ', alternate_venue_1)
#         print('alternate_venue_2 : ', alternate_venue_2)
        


#         request = Request.objects.create(
#             venue=venue,
#             user=user_id,
#             date=date,
#             time=time,  
#             duration=duration,
#             alternate_venue_1=alternate_venue_1,
#             alternate_venue_2=alternate_venue_2,
#             event_details=event_details,
#             need=need
#         )
#         return request.id  # Returning request ID for reference
#     except Venue.DoesNotExist:
#         raise ValueError("Venue doesn't exist")



from users.models import CustomUser

def requestSlotFromDB(venue_id, user_id, date, time, duration, alternate_venues, event_details, need):
    try:
        # Get main venue
        venue = Venue.objects.get(id=venue_id)
        print('venue: ', venue)  # Debugging log

        # Get user details
        user = CustomUser.objects.get(id=user_id)

        # Determine request status based on role
        if user.role == 'student':  
            initial_status = 'waiting_for_approval'  # Students require faculty approval
        else:
            initial_status = 'pending'  # Faculty and others get direct approval

        # Get alternate venues (handle cases where alternate_venues may be empty)
        alternate_venue_1 = Venue.objects.get(id=alternate_venues[0]) if alternate_venues and alternate_venues[0] else None
        alternate_venue_2 = Venue.objects.get(id=alternate_venues[1]) if alternate_venues and len(alternate_venues) > 1 else None

        # Debugging logs
        print('alternate_venue_1:', alternate_venue_1)
        print('alternate_venue_2:', alternate_venue_2)
        print('user_id:', user_id)
        print('date:', date)
        print('time:', time, '| Type:', type(time))
        print('duration:', duration)
        print('event_details:', event_details)
        print('need:', need)
        print('Initial Status:', initial_status)  # Debugging log

        # Creating the request object
        request = Request.objects.create(
            venue=venue,
            user=user,
            date=date,
            time=time,  
            duration=duration,
            alternate_venue_1=alternate_venue_1,
            alternate_venue_2=alternate_venue_2,
            event_details=event_details,
            need=need,
            status=initial_status  # Set the initial status based on role
        )

        print('Request ID:', request.request_id)  # Debugging log
        return request.request_id  # Returning request ID for reference

    except Venue.DoesNotExist:
        raise ValueError("Venue doesn't exist")
    except CustomUser.DoesNotExist:
        raise ValueError("User doesn't exist")


def forwardRequestToGymkhanaFromDB(request_id, user_id):
    user = CustomUser.objects.get(id=user_id)
    req = Request.objects.get(request_id=request_id)
    # add a check for user role
    if (req.status != 'waiting_for_approval'):
        raise ValueError('Cannot Forward a Request that is already Forwarded')
    
    user_req=req.user

    if (user.organization_name != user_req.organization_name):
        raise ValueError("Cannot Approve Requests other than your Organization")
    
    req.status='pending'
    req.save()

    return True

def getForwardRequestsFromDB(user_id):
    try:
        # Fetch the user making the query
        user = CustomUser.objects.get(id=user_id)

        # Fetch all requests that are waiting for approval
        requests = Request.objects.filter(status="waiting_for_approval").values(
            "request_id", "user__name", "venue__venue_name", "date", "time", "duration", "event_details"
        )

        return list(requests)  # Convert queryset to list of dictionaries

    except CustomUser.DoesNotExist:
        raise ValueError("User not found")


'''
class Request(models.Model):
    STATUS_CHOICES = [
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
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')  # Request status
    reasons = models.CharField(max_length=255, blank=True, null=True)  # Reason for approval/rejection
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Request {self.request_id} by {self.user} for {self.venue}"

'''


def getBookedSlotsFromDB(venue_id, start_date, end_date):
    return list(Booking.objects.filter(
        venue_id=venue_id, 
        date__range=[start_date, end_date]
    ).exclude(status="cancelled")  # Exclude cancelled bookings
    .values('date', 'time', 'duration'))


def cancelRequestFromDB(req_id):
    try:
        request = Request.objects.get(request_id=req_id)

        if request.status != "approved":
            # If the request is not approved, simply mark it as "cancelled"
            request.status = "cancelled"
            request.save()
            return True

        # If the request is approved, cancel the booking as well
        booking = Booking.objects.filter(request=request).first()
        if booking:
            booking.status = "cancelled"
            booking.save()

        # Now cancel the request
        request.status = "cancelled"
        request.save()

        return True  # Successfully cancelled

    except Request.DoesNotExist:
        return False  # Request ID not found

""" 
# ✅ Cancel request (No changes needed)
def cancelRequestFromDB(req_id):
    with connection.cursor() as cursor:
        cursor.execute(query, (req_id,))
        connection.commit()
    return True
 """

def declineForwardRequestFromDB(request_id, user_id):
    user = CustomUser.objects.get(id=user_id)
    req = Request.objects.get(request_id=request_id)
    # add a check for user role
    if (req.status != 'waiting_for_approval'):
        raise ValueError('Cannot Forward a Request that is already Forwarded')
    
    user_req=req.user

    if (user.organization_name != user_req.organization_name):
        raise ValueError("Cannot Approve Requests other than your Organization")
    
    req.status='rejected'
    req.save()

    return True
