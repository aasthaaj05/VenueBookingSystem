

from django.db import connection
import uuid



# ✅ Get venue details as JSON
# ✅ Returns JSON-like list of dictionaries



import uuid



from request_booking.models import Venue, Request
from gymkhana.models import Booking

def getVenuesFromDB(limit):
    return list(Venue.objects.all()[:limit].values('venue_name', 'facilities', 'photo_url'))

def getVenueDetailsFromDB(venue_id):
    venue = Venue.objects.filter(id=venue_id).values().first()
    return venue if venue else None

def getUserRequestsFromDB(user_id):
    return list(Request.objects.filter(user_id=user_id).values('id', 'date', 'time', 'duration', 'status', 'venue__venue_name'))





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
    print('in services : db.py forwardRequestToGymkhanaFromDB() ')
    user = CustomUser.objects.get(id=user_id)
    req = Request.objects.get(request_id=request_id)

    if user.role.lower() == 'faculty_advisor':
    # add a check for user role
        if (req.status != 'waiting_for_approval'):
            raise ValueError('Cannot Forward a Request that is already Forwarded')
        
        user_req=req.user

        if (user.organization_name != user_req.organization_name):
            raise ValueError("Cannot Approve Requests other than your Organization")
        
        req.status='pending'
        req.save()

        return True
    elif user.role.lower() == 'venue_admin':
        if (req.status != 'pending'):
            raise ValueError('Cannot Forward a Request that is not forwarded')
        
        user_req=req.user

     
        
        req.status='accepted'
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





def getBookedSlotsFromDB(venue_id, start_date, end_date):
    return list(Booking.objects.filter(
        venue_id=venue_id, 
        date__range=[start_date, end_date]
    ).exclude(status="cancelled")  # Exclude cancelled bookings
    .values('date', 'time', 'duration'))

from django.db.models import Q

# def getBookedSlotsFromDB(venue_name, date):
#     venue = Venue.objects.get(venue_name=venue_name)
#     return list(
#         Booking.objects.filter(
#             venue=venue,
#             date=date
#         ).exclude(
#             Q(status="cancelled") | Q(status="user-cancelled")
#         ).values('date', 'time', 'duration')
#     )


def getBookedSlotsFromDB1(venue_name, date):
    venue = Venue.objects.get(venue_name=venue_name)
    return list(
        Booking.objects.filter(
            venue=venue,
            date=date,
            status='active'  # Only include active bookings
        ).values('date', 'time', 'duration')
    )




# def getBookedSlotsFromDB1(venue_name, date):
#     venue=Venue.objects.get(venue_name=venue_name)
#     return list(Booking.objects.filter(
#         venue=venue, 
#         date=date
#     ).exclude(status="cancelled")  # Exclude cancelled bookings
#     .values('date', 'time', 'duration'))



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



def declineForwardRequestFromDB(request_id, user_id):
    print('in services : declineForwardRequestFromDB() ')
    user = CustomUser.objects.get(id=user_id)
    req = Request.objects.get(request_id=request_id)

    if user.role.lower() == 'faculty_advisor':
        print('user role : faculty_advisor')
        
        # add a check for user role
        if (req.status != 'waiting_for_approval'):
            raise ValueError('Cannot Forward a Request that is already Forwarded')
        
        user_req=req.user

        if (user.organization_name != user_req.organization_name):
            raise ValueError("Cannot Approve Requests other than your Organization")
        
        req.status='rejected'
        req.save()

        return True

    elif user.role.lower() == 'venue_admin':
        print('user role : venue_admin')

        # add a check for user role
        if (req.status != 'pending'):
            raise ValueError('Cannot Forward a Request that is already not approved')
        
        user_req=req.user

        
        
        req.status='rejected'
        req.save()

        return True

    return True
