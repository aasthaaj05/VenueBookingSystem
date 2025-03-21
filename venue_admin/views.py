from django.shortcuts import render

# Create your views here.
from django.shortcuts import get_object_or_404, get_list_or_404, render, redirect
from django.db import transaction
from django.db.models import Q
from django.contrib import messages

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from collections import defaultdict
import uuid

# from .models import Request, Booking, Venue, Rejection, RejectedBooking
from gymkhana.serializers import (
    VenueSerializer,
    RequestSerializer,
    RejectionSerializer,
)
from gymkhana.models import Request, Booking, Venue, Rejection, RejectedBooking
from users.models import CustomUser
from django.views.decorators.csrf import csrf_exempt




sender_email = "arnavp22.comp@coeptech.ac.in"  # Outlook Email
sender_password = "!gui2#@lk1!gui2#@lk1"      # Outlook Email Password
smtp_server = "smtp.office365.com"
smtp_port = 587  # Outlook SMTP port


def home(request):
    return render(request , 'venue_admin/index.html')



def get_requests(request):
    # Logic for handling view requests
    return render(request, 'venue_admin/venue_admin_get_pending_requests.html')


from django.shortcuts import render, redirect
from django.contrib import messages
from gymkhana.models import Venue
from request_booking.models import Request



from django.contrib.auth import logout
from django.shortcuts import redirect

def logout_view(request):
    # Clear the session data
    request.session.flush()
    
    # Logout the user
    logout(request)
    
    # Redirect to login or homepage
    return redirect('/users/login')  # Change 'login' to the actual login page name



from django.http import JsonResponse

def reject_request(request, request_id):
    print("""Reject a request and store the reason in the rejection table.""")
    req = get_object_or_404(Request, request_id=request_id)

    print("""23r23fr23frq23r Reject a request and store the reason in the rejection table.""")

    if req.status != 'pending':
        return JsonResponse({"error": "Request is not in a pending state."}, status=400)

    print("#############################################Req found!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")

    req.status = 'rejected'
    req.reasons = ''
    req.save()

    rejection = Rejection.objects.create(
        request=req,
        user=req.user,
        msg='Slot already booked'
    )

    # ✅ Send rejection email to requester
    send_booking_rejected_email(req)

    data = {
        "message": "Request rejected successfully.",
        "rejection": RejectionSerializer(rejection).data
    }


    # return JsonResponse(data, status=200)
    return redirect('/venue_admin/requests')



@api_view(['POST'])
# @permission_classes([IsAuthenticated])
def cancel_request(request, request_id):
    """Cancel a request."""
    req = get_object_or_404(Request, request_id=request_id)

    if req.status not in ['pending', 'approved']:
        return Response({"error": "Request cannot be canceled."}, status=status.HTTP_400_BAD_REQUEST)

    req.status = 'cancelled'
    req.save()

    return Response({"message": "Request cancelled successfully."}, status=status.HTTP_200_OK)




@api_view(['GET'])
# @permission_classes([IsAuthenticated])
def pending_requests_by_date(request):
    """
    Fetch all pending requests and group them by date.
    The response format: { "YYYY-MM-DD": [list of pending requests] }
    """
    pending_requests = Request.objects.filter(status='pending').order_by('date', 'time')

    if not pending_requests.exists():
        return Response({"message": "No pending requests."}, status=status.HTTP_200_OK)

    grouped_requests = defaultdict(list)
    
    for req in pending_requests:
        grouped_requests[str(req.date)].append(RequestSerializer(req).data)

    return Response(grouped_requests, status=status.HTTP_200_OK)



@api_view(['GET'])  # Accept user_id in the request body
def requests_for_venue(request):
    """
    Get all venue requests assigned to the gymkhana member based on `user_id`.
    """
    user_id = request.data.get("user_id")  # Get user_id from request body

    if not user_id:
        return Response({"error": "user_id is required"}, status=status.HTTP_400_BAD_REQUEST)

    # Ensure user_id is a valid UUID (if using UUIDs in CustomUser)
    try:
        venue_user = get_object_or_404(CustomUser, id=user_id)
    except ValueError:
        return Response({"error": "Invalid user_id format"}, status=status.HTTP_400_BAD_REQUEST)

    # Find venues assigned to this Gymkhana department in-charge
    venues = Venue.objects.filter(department_incharge=venue_user)

    if not venues.exists():
        return Response({"message": "No venues assigned to this user."}, status=status.HTTP_404_NOT_FOUND)

    # Get all pending requests for those venues
    requests = Request.objects.filter(venue__in=venues).order_by('date', 'time')

    if not requests.exists():
        return Response({"message": "No requests found for your venues."}, status=status.HTTP_200_OK)

    # Group requests by date for better frontend display
    grouped_requests = defaultdict(list)
    for req in requests:
        grouped_requests[str(req.date)].append(RequestSerializer(req).data)

    return Response(grouped_requests, status=status.HTTP_200_OK)




def request_booking(request): 
    user = request.user
    try:
        # ✅ Fetch user from CustomUser model
        user = CustomUser.objects.get(email=user)
    except CustomUser.DoesNotExist:
        return render(request, 'faculty_advisor/pending_requests.html', {
            'requests': []
        })

    # ✅ Filter requests where status is 'pending' OR 'waiting for approval'
    requests = Request.objects.select_related('venue', 'user').filter(
        Q(status="pending"),
        venue__department_incharge=user
    )


    context = {
        'pending_requests': [
            {
                'request_id': str(req.request_id),
                'date': req.date.strftime('%Y-%m-%d'),
                'time': f"{req.time}:00",  # Format time as HH:00
                'duration': f"{req.duration} hours",  # ✅ Include duration directly
                'venue': {
                    'venue_name': req.venue.venue_name if req.venue else 'Unknown Venue',
                    'capacity': req.venue.capacity if req.venue else 'N/A',
                },
                'user': {
                    'name': req.user.name if req.user else 'Unknown',
                    'organization_name': req.user.organization_name if req.user else 'Unknown'
                },
                'event_details': req.event_details if req.event_details else 'N/A',
                'status': req.status,
                'reasons': req.reasons if req.status == 'rejected' else None,
                'purpose': req.need if req.need else 'N/A'
            }
            for req in requests
        ]
    }

    print('context : ', context)  # Debugging output

    return render(request, 'venue_admin/venue_admin_get_pending_requests.html', context)




import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

def send_booking_accepted_email(req):
    print()
    print()
    print('--------start : send_booking_accepted_email-----------')
    requester_email = req.user.email  # Get requester's email
    print('requester_email : ' , requester_email)

    if not requester_email:
        print("Requester email not found.")
        return

    

    # Email content
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = requester_email
    msg['Subject'] = "Venue Booking Approved ✅"

    body = f"""
    Dear {req.user.name},

    Your venue booking request has been approved! 🎉

    Booking Details:
    - Booking ID: {req.request_id}
    - Venue: {req.venue.venue_name}
    - Date: {req.date}
    - Time: {req.time}
    - Duration: {req.duration} hours
    - Event Details: {req.event_details}

    Please ensure you arrive on time and follow the venue guidelines.

    If you have any questions, feel free to contact the venue in-charge.

    Regards,  
    COEP Venue Booking System
    """

    msg.attach(MIMEText(body, 'plain'))

    # Send email
    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.send_message(msg)

        print(f"Booking approval email sent to {requester_email}")
    except Exception as e:
        print(f"Failed to send email: {e}")


    print('-----end send_booking_accepted_email--------')
    print()
    print()

# Example usage:
# send_booking_accepted_email(req)



import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

def send_booking_rejected_email(req):
    print()
    print()
    print('--------start : send_booking_rejected_email-----------')
    requester_email = req.user.email  # Get requester's email
    print('requester_email : ', requester_email)

    if not requester_email:
        print("Requester email not found.")
        return

    # Email content
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = requester_email
    msg['Subject'] = "Venue Booking Rejected ❌"

    body = f"""
    Dear {req.user.name},

    We regret to inform you that your venue booking request has been rejected due to scheduling conflicts.  

    Request Details:
    - Booking ID: {req.request_id}
    - Venue: {req.venue.venue_name}
    - Date: {req.date}
    - Time: {req.time}:00
    - Duration: {req.duration} hours
    - Event Details: {req.event_details}

    Reason for Rejection: The requested venue is unavailable at the specified time.  

    What you can do next?
    - Try booking a different venue.  
    - Choose an alternative date/time.  
    - Contact the venue in-charge for further assistance.

    We apologize for the inconvenience. Feel free to reach out for any queries.

    Regards,  
    COEP Venue Booking System
    """

    msg.attach(MIMEText(body, 'plain'))

    # Send email
    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.send_message(msg)

        print(f"Booking rejection email sent to {requester_email}")
    except Exception as e:
        print(f"Failed to send email: {e}")

    print('-----end send_booking_rejected_email--------')
    print()
    print()





import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

def send_request_forwarded_email(req, new_venue):
    print()
    print()
    print("\n-------- Start: send_request_forwarded_email --------")
    
    requester_email = req.user.email  # Get requester's email
    print('Requester Email:', requester_email)

    if not requester_email:
        print("Requester email not found.")
        return

    # Email content
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = requester_email
    msg['Subject'] = "Venue Booking Request Forwarded 🔄"

    body = f"""
    Dear {req.user.name},

    Your venue booking request for {req.venue.venue_name} on {req.date} at {req.time} could not be accommodated due to a scheduling conflict. 

    However, we have forwarded your request to an alternative venue:  
    {new_venue.venue_name}  

    Your request is now under review for the new venue, and we will notify you once a decision is made.

    New Request Details:
    - Venue: {new_venue.venue_name}
    - Date: {req.date}
    - Time: {req.time}
    - Duration: {req.duration} hours
    - Event Details: {req.event_details}

    If you have any concerns or need further assistance, feel free to contact us.

    Regards,  
    COEP Venue Booking System
    """

    msg.attach(MIMEText(body, 'plain'))

    # Send email
    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.send_message(msg)

        print(f"Forwarding email sent to {requester_email}")
    except Exception as e:
        print(f"Failed to send email: {e}")

    print("-------- End: send_request_forwarded_email --------\n")
    print()
    print()






import uuid
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from gymkhana.models import Request, Booking
from gymkhana.serializers import BookingSerializer

def forward_request_to_alternate(request):

    print('.........in forward_request_to_alternate().......')
    if request.alternate_venue_1:
        # Create a new request based on the existing one
        new_request = Request.objects.create(
            user=request.user,
            date=request.date,
            time=request.time,
            duration=request.duration,
            venue=request.alternate_venue_1,
            need=request.need,
            alternate_venue_1=request.alternate_venue_2,
            alternate_venue_2=None,
            event_details=request.event_details,
            status='pending',
            reasons="Forwarded from another venue"
        )
        # Update the original request status
        request.status = 'forwarded'
        request.save()

        # ✅ Send email to notify requester about forwarding
        send_request_forwarded_email(request, new_request.venue)

        return new_request
    else:
        request.status = 'rejected'
        request.reasons = 'Slot is unavailable due to conflicting booking.'
        request.save()
        Rejection.objects.create(
            request=request,
            user=request.user,
            reason='Slot is unavailable due to conflicting booking.',
            msg='Booking conflict with another approved request.'
        )
        
    print('.........Ended in forward_request_to_alternate().......')

def approve_request(request, request_id):
    print()
    print()
    print('-------in approve_request()-------')

    if request.method == "POST":
        req = get_object_or_404(Request, request_id=request_id)
        start_time = req.time
        end_time = req.time + req.duration
        user=CustomUser.objects.get(email=request.user)
        pending_requests = Request.objects.filter(
            venue=req.venue,
            date=req.date,
            status='pending',
            venue__department_incharge=user,
            ).exclude(request_id=req.request_id)

        conflicting_requests = []
        for existing in pending_requests:
            existing_start = existing.time
            existing_end = existing.time + existing.duration
            
            # ✅ Overlap conditions for slot-based conflict:
            if (existing_end > start_time and existing_end < end_time) or (existing_start < end_time and existing_start > start_time)  :
                conflicting_requests.append(existing)

        if conflicting_requests:
            # Reject all conflicting requests
            for conflict in conflicting_requests:
                forward_request_to_alternate(conflict)



        # Prepare data for serializer
        booking_data = {
            "booking_id": uuid.uuid4(),  # ✅ Ensure new UUID is assigned
            "request": str(req.request_id),  # ✅ Directly pass request object (since it's a OneToOneField)
            "user": str(req.user.id),
            "date": req.date,
            "time": req.time,
            "duration": req.duration,
            "venue": str(req.venue.id),
            "event_details": req.event_details
        }

        serializer = BookingSerializer(data=booking_data)

        if serializer.is_valid():
            with transaction.atomic():
                booking = serializer.save()  # Save Booking
                
                # ✅ Update request status to "approved" instead of deleting
                req.status = "approved"
                req.save(update_fields=["status"])

                print("✅ Booking saved successfully, request updated!")  # Debugging
                messages.success(request, "Booking approved and request status updated!")

                send_booking_accepted_email(req)
                print()
                print()

            return redirect('/venue_admin/requests')
        else:
            print("❌ Serializer errors:", serializer.errors)  # Debugging
            messages.error(request, "Error approving request.")

    return redirect('/venue_admin/requests')




def approved_bookings_view(request):
    user_id = request.user.id
    
    # ✅ Get the user (already logged in)
    try:
        user = CustomUser.objects.get(id=user_id)
    except CustomUser.DoesNotExist:
        return render(request, 'venue_admin/approved_bookings.html', {
            'user': None,
            'managed_venues': [],
            'approved_bookings': []
        })

    # ✅ Get venues managed by the user
    managed_venues = Venue.objects.filter(department_incharge=user)

    # ✅ Get approved bookings for those venues
    approved_bookings = Booking.objects.filter(
        venue__in=managed_venues,
        status='active'
    ).select_related('user', 'venue')


    # ✅ Pass data to context
    context = {
        'user': user,
        'managed_venues': managed_venues,
        'approved_bookings': approved_bookings
    }

    return render(request, 'venue_admin/approved_bookings.html', context)