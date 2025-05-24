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

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from django.conf import settings  # Import settings




sender_email = settings.EMAIL_HOST_USER
sender_password = settings.EMAIL_HOST_PASSWORD
smtp_server = settings.EMAIL_HOST
smtp_port = settings.EMAIL_PORT


def home(request):
    return render(request , 'venue_admin/index.html')



def get_requests(request):
    # Logic for handling view requests
    return render(request, 'venue_admin/venue_admin_get_pending_requests.html')

def get_cumulative_requests(request):
    # Logic for handling view requests
    return render(request, 'venue_admin/get_cumulative_requests.html')
    


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


from django.shortcuts import get_object_or_404, redirect
from django.http import JsonResponse
import logging
from django.http import JsonResponse

logger = logging.getLogger(__name__)

def reject_request(request, request_id):
    print("""Reject a request and store the reason in the rejection table.""")
    req = get_object_or_404(Request, request_id=request_id)

    print("""23r23fr23frq23r Reject a request and store the reason in the rejection table.""")

    print("Form data (POST):", request.POST)
    print("GET data (URL params):", request.GET)
    print("User:", request.user)
    print("Headers:", request.headers)



    if req.status != 'pending':
        return JsonResponse({"error": "Request is not in a pending state."}, status=400)

    print("#############################################Req found!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")

    reason = request.POST.get("feedback_reason", "")
    feedback_from_admin = request.POST.get("feedback_comments", "")
    alternate_venues_suggestion = request.POST.get("alternative_options", "")
    print('reason : ', reason)
    print('comments : ' , feedback_from_admin)
    print('alternatives : ' , alternate_venues_suggestion)
    print()
    print()

    # ✅ Construct message (optional formatting, you can change this)
    full_msg = f"{feedback_from_admin}\n\nSuggested Alternatives:\n{alternate_venues_suggestion}".strip()

    # ✅ Update request and create rejection
    req.status = 'rejected'
    req.reasons = reason
    req.save()

    rejection = Rejection.objects.create(
        request=req,
        user=req.user,
        reason=reason,
        msg=full_msg,
        feedback_from_admin = feedback_from_admin,
        alternate_venues_suggestion = alternate_venues_suggestion,
    )

    # ✅ Send rejection email to requester
    # send_booking_rejected_email(req)
    try:
        send_booking_rejected_email(req, full_msg)
    except Exception as e:
        logger.error(f"Failed to send rejection email for request {request_id}: {e}")
        # Optionally alert admin or show a warning in UI

    data = {
        "message": "Request rejected successfully.",
        "rejection": RejectionSerializer(rejection).data
    }


    # return JsonResponse(data, status=200)
    return redirect('/venue_admin/requests')

def reject_cumulative_request(request, cumulative_request_id):
    print()
    print("-------in reject_cumulative_request()-------")
    print("Method:", request.method)
    print()

    if request.method == "POST":
        print('POST data received in reject_cumulative_request():')
        for key, value in request.POST.items():
            print(f"{key}: {value}")

        reason = request.POST.get("feedback_reason", "")
        feedback_from_admin = request.POST.get("feedback_comments", "")
        alternate_venues_suggestion = request.POST.get("alternative_options", "")

        print("Reason:", reason)
        print("Admin Feedback:", feedback_from_admin)
        print("Alternatives:", alternate_venues_suggestion)

        cumulative_req = get_object_or_404(CumulativeRequest, cumulative_request_id=cumulative_request_id)
        individual_requests = Request.objects.filter(
            cumulative_request_id=cumulative_request_id,
            status='pending'  # Only reject pending requests
        )

        if not individual_requests.exists():
            messages.error(request, "No pending requests found for this cumulative booking.")
            return redirect('/venue_admin/cumulative_requests')

        store_rejection_msg=""

        with transaction.atomic():
            for req in individual_requests:
                req.status = 'rejected'
                req.reasons = reason
                req.save(update_fields=["status", "reasons"])

                rejection = Rejection.objects.create(
                    request=req,
                    user=req.user,
                    reason=reason,
                    msg=f"{feedback_from_admin}\n\nSuggested Alternatives:\n{alternate_venues_suggestion}".strip(),
                    feedback_from_admin=feedback_from_admin,
                    alternate_venues_suggestion=alternate_venues_suggestion,
                )
                store_rejection_msg = rejection.msg

                # # Send rejection email
                # try:
                #     # send_booking_rejected_email(req, rejection.msg)
                # except Exception as e:
                #     logger.error(f"Failed to send rejection email for request {req.request_id}: {e}")

            cumulative_req.status = 'rejected'
            cumulative_req.reasons = reason
            cumulative_req.save(update_fields=["status", "reasons"])

            send_cumulative_booking_rejected_email(req, cumulative_req,store_rejection_msg)

            messages.success(request, "Cumulative booking and all its requests have been rejected.")
            print("✅ Cumulative booking rejected successfully")

        return redirect('/venue_admin/cumulative_requests')

    return redirect('/venue_admin/cumulative_requests')


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



import json



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
        cumulative_booking=0,
    )


    context = {
        'pending_requests': [
            {
                'request_id': str(req.request_id),
                'email':req.email,
                'phone_number':req.phone_number,
                'event_type':req.event_type,
                'date': req.date.strftime('%Y-%m-%d'),
                'time': f"{req.time}:00",  # Format time as HH:00
                'duration': f"{req.duration}",  # ✅ Include duration directly
                'venue': {
                    'venue_name': req.venue.venue_name if req.venue else 'Unknown Venue',
                    'capacity': req.venue.capacity if req.venue else 'N/A',
                },
                'user': {
                    'name': req.user.name if req.user else 'Unknown',
                    'organization_name': req.user.organization_name if req.user else 'Unknown'
                },
                'guest_count':req.guest_count,
                'event_details': req.event_details if req.event_details else 'N/A',
                'status': req.status,
                'reasons': req.reasons if req.status == 'rejected' else None,
                'purpose': req.need if req.need else 'N/A',
                'additional_info':req.additional_info,
                'special_requirements':req.special_requirements,
                'need':req.need,
            }
            for req in requests
        ]
    }

    # print('context : ', context)  # Debugging output
    print("Context:")
    print(json.dumps(context, indent=4))

    print('[]][][][][]')


    return render(request, 'venue_admin/venue_admin_get_pending_requests.html', context)
    # return render(request, 'venue_admin/venue_admin_get_pending_requests.html', {
    #     'pending_requests': json.dumps(context['pending_requests'])
    # })

from request_booking.models import CumulativeRequest



from request_booking.models import CumulativeRequest
from django.db.models import Q

def cumulative_request_booking(request): 
    user = request.user
    try:
        # Fetch user from CustomUser model
        user = CustomUser.objects.get(email=user)
    except CustomUser.DoesNotExist:
        return render(request, 'faculty_advisor/pending_requests.html', {
            'requests': []
        })

    # Fetch cumulative requests with status 'waiting_for_approval' or 'pending'
    cumulative_requests = CumulativeRequest.objects.select_related('venue', 'user').filter(
        Q(status="waiting_for_approval") | Q(status="pending"),
        # venue__department_incharge=user
    ).order_by('-created_at')
    print('cumulative_requests : ', cumulative_requests)

    # Prepare the context data
    pending_cumulative_requests = []
    for cr in cumulative_requests:
        # Get all individual requests associated with this cumulative request
        individual_requests = Request.objects.filter(
            cumulative_request_id=cr.cumulative_request_id
        ).select_related('venue', 'user')
        
        # Format dates for display
        dates = [req.date.strftime('%Y-%m-%d') for req in individual_requests]

         # Step 1: Clean and deduplicate the weekday numbers
        clean_weekdays = list(dict.fromkeys(cr.weekdays.split(',')))

        # Step 2: Mapping numbers to weekday names
        weekday_map = {
            '0': 'Monday',
            '1': 'Tuesday',
            '2': 'Wednesday',
            '3': 'Thursday',
            '4': 'Friday',
            '5': 'Saturday',
            '6': 'Sunday'
        }

        # Step 3: Get list of weekday names
        weekday_names = [weekday_map[num] for num in clean_weekdays if num in weekday_map]

        # Step 4: Create comma-separated string
        weekday_str = ', '.join(weekday_names)

        # Print result
        print('clean_weekdays :', clean_weekdays)
        print('weekday_names :', weekday_names)
        print('weekday_str :', weekday_str)


        
        pending_cumulative_requests.append({
            'cumulative_request_id': str(cr.cumulative_request_id),
            'email': cr.email or cr.user.email,
            'phone_number': cr.phone_number or cr.user.phone_number,
            'event_type': cr.event_type,
            'dates': dates,  # All dates from individual requests
            'start_date': cr.start_date.strftime('%Y-%m-%d'),
            'weekdays': weekday_str,  # String representation of weekdays
            'time': f"{cr.time}:00",
            'duration': f"{cr.duration}",
            'num_weeks': cr.num_weeks,
            'venue': {
                'venue_name': cr.venue.venue_name if cr.venue else 'Unknown Venue',
                'capacity': cr.venue.capacity if cr.venue else 'N/A',
            },
            'user': {
                'name': cr.user.name if cr.user else 'Unknown',
                'organization_name': cr.user.organization_name if cr.user else 'Unknown'
            },
            'guest_count': cr.guest_count,
            'event_details': cr.event_details if cr.event_details else 'N/A',
            'status': cr.status,
            'reasons': cr.reasons if cr.status == 'rejected' else None,
            'purpose': cr.purpose if cr.purpose else 'N/A',
            # 'additional_info': cr.additional_info,
            'additional_info': individual_requests.first().additional_info if individual_requests.exists() else 'N/A',
            'special_requirements': cr.special_requirements,
            'individual_request_count': individual_requests.count(),  # How many individual requests
            'individual_requests': [str(req.request_id) for req in individual_requests]  # List of request IDs
        })

    context = {
        'pending_requests': pending_cumulative_requests
    }

    print("Cumulative Context:")
    print(json.dumps(context, indent=4))
    print('====END OF CONTEXT====')

    return render(request, 'venue_admin/get_cumulative_requests.html', context)





import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# New function to notify venue in-charge
def send_booking_accepted_email_to_incharge(req):
    print('\n--------start : send_booking_accepted_email_to_incharge-----------')
    print('\n--------start : send_booking_accepted_email_to_incharge-----------')
    print('\n--------start : send_booking_accepted_email_to_incharge-----------')

    venue = req.venue
    incharge_email = venue.dept_incharge_email
    print('incharge_email : ', incharge_email)

    if not incharge_email:
        print("In-charge email not found.")
        return

    requester_name = req.user.name
    requester_email = req.user.email
    requester_phone_number = req.phone_number

    print('requester_name : ', requester_name)
    print('requester_email : ', requester_email)
    print('requester_phone_number : ', requester_phone_number)

    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = incharge_email
    print('//----sender_email : ', sender_email)
    print('incharge_email : ', incharge_email)
    msg['Subject'] = "Booking Confirmed for Your Venue"

    body = f"""
    Dear {venue.department_incharge.name if venue.department_incharge else 'In-charge'},

    A venue booking request for your venue has been approved.

    Booking Details:
    - Booking ID: {req.request_id}
    - Venue: {venue.venue_name}
    - Date: {req.date}
    - Time: {req.time}
    - Duration: {req.duration} hours
    - Event Details: {req.event_details}

    Requester Information:
    - Name: {requester_name}
    - Email: {requester_email}
    - Phone Number : {requester_phone_number}

    Please ensure the venue is accessible and ready at the scheduled time.

    Regards,  
    COEP Venue Booking System
    """

    msg.attach(MIMEText(body, 'plain'))
    print('Send email')
    with smtplib.SMTP(smtp_server, smtp_port) as server:
        server.starttls()
        server.login(sender_email, sender_password)
        server.send_message(msg)

    # try:
    #     server = smtplib.SMTP(smtp_server, smtp_port)
    #     print('poipipio')
    #     server.starttls()
    #     print('starttls , starttls , starttls , starttls , starttls')
    #     print('sender_password : ', sender_password)
    #     print('sender_email : ', sender_email)
    #     server.login(sender_email, sender_password)
    #     print('login ., login , login , login , login , login')
    #     # server.sendmail(sender_email, incharge_email, msg.as_string())
    #     # print('sendmail , sendmail , sendmail , sendmail , sendmail')
    #     # server.quit()
    #     server.send_message(msg)
    #     print("Email sent successfully to in-charge.")
    # except Exception as e:
    #     print("Failed to send email to in-charge:", e)





# # send_booking_accepted_email(req , feedback_reason , feedback_comments)
# def send_booking_accepted_email(req , feedback_reason , feedback_comments):
#     print()
#     print()
#     print('--------start : send_booking_accepted_email-----------')
#     requester_email = req.user.email  # Get requester's email
#     print('requester_email : ' , requester_email)
#     print('venue incharge mail', req.venue.dept_incharge_email)

#     if not requester_email:
#         print("Requester email not found.")
#         return

#     # Get incharge contact info from venue
#     venue = req.venue
#     incharge_email = venue.dept_incharge_email or "Not available"
#     incharge_phone = venue.dept_incharge_phone or "Not available"

#     print('incharge_email : ',incharge_email)
#     print('incharge_phone : ', incharge_phone)

    

#     # Email content
#     msg = MIMEMultipart()
#     msg['From'] = sender_email
#     msg['To'] = requester_email
#     print('sender_email : ', sender_email)
#     print('requester_email : ', requester_email)
#     msg['Subject'] = "Venue Booking Approved ✅"

#     body = f"""
#     Dear {req.user.name},

#     Your venue booking request has been approved! 🎉

#     Booking Details:
#     - Booking ID: {req.request_id}
#     - Venue: {req.venue.venue_name}
#     - Date: {req.date}
#     - Time: {req.time}
#     - Duration: {req.duration} hours
#     - Event Details: {req.event_details}

#     Feedback from Admin:
#     - Feedback : {feedback_reason}
#     - Comments : {feedback_comments}

#     Please ensure you arrive on time and follow the venue guidelines.

#     If you have any questions, feel free to contact the venue in-charge to ensure your needs for the venue are met.

#     Venue In-Charge Contact:
#     - Email: {incharge_email}
#     - Phone: {incharge_phone}

#     Regards,  
#     COEP Venue Booking System
#     """

#     msg.attach(MIMEText(body, 'plain'))

#     # Send email
#     try:
#         with smtplib.SMTP(smtp_server, smtp_port) as server:
#             server.starttls()
#             server.login(sender_email, sender_password)
#             server.send_message(msg)

#         print(f"Booking approval email sent to {requester_email}")
#     except Exception as e:
#         print(f"Failed to send email: {e}")


#     print('-----end send_booking_accepted_email--------')
#     # Call new function to notify the in-charge
#     send_booking_accepted_email_to_incharge(req)

#     print()
#     print()


import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from django.utils.timezone import now


def send_booking_accepted_email(req, feedback_reason, feedback_comments):
    print('\n\n--------start : send_booking_accepted_email-----------')
    print('\n\n--------start : send_booking_accepted_email-----------')
    print('\n\n--------start : send_booking_accepted_email-----------')
    print('\n\n--------start : send_booking_accepted_email-----------')
    requester_email = req.user.email  # Get requester's email
    print('requester_email : ', requester_email)
    print('venue incharge mail', req.venue.dept_incharge_email)

    if not requester_email:
        print("Requester email not found.")
        return

    # Get incharge contact info from venue
    venue = req.venue
    incharge_email = venue.dept_incharge_email or "Not available"
    incharge_phone = venue.dept_incharge_phone or "Not available"

    print('incharge_email : ', incharge_email)
    print('incharge_phone : ', incharge_phone)

    

    # Email content
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = requester_email
    print('sender_email : ', sender_email)
    print('requester_email : ', requester_email)
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

    Feedback from Admin:
    - Feedback : {feedback_reason}
    - Comments : {feedback_comments}

    Please ensure you arrive on time and follow the venue guidelines.

    If you have any questions, feel free to contact the venue in-charge to ensure your needs for the venue are met.

    Venue In-Charge Contact:
    - Email: {incharge_email}
    - Phone: {incharge_phone}

    Regards,  
    COEP Venue Booking System
    """

    msg.attach(MIMEText(body, 'plain'))

    # Send email
    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            print('sender_email : ', sender_email)
            print('sender_password : ', sender_password)
            print('type(sender_email) : ', type(sender_email))
            print('type(sender_password) : ', type(sender_password))
            server.starttls()
            print('*********')
            
            server.login(sender_email, sender_password)
            
            print('//111//111//222/!!')
            server.send_message(msg)
            print('sender_email : ', sender_email)
            print('sender_password : ', sender_password)
            print(f"Booking approval email sent to {requester_email}")
    except Exception as e:
        print(f"Failed to send email: {e}")
    finally:
        print('-----end send_booking_accepted_email--------')
        # Call new function to notify the in-charge
        send_booking_accepted_email_to_incharge(req)
        print('\n\n')




# Example usage:
# send_booking_accepted_email(req)




import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# Replace with your actual SMTP credentials
smtp_server = 'smtp.gmail.com'
smtp_port = 587

def venue_admin_send_cumulative_booking_accepted_email(req, cumulative_req,feedback_reason, feedback_comments):
    print('\n--------start : venue_admin_send_cumulative_booking_accepted_email-----------')
    print(req)
    # print(json.dumps(req, indent=4))  # Nicely formatted JSON-style print

    # Use email from request row directly
    requester_email = cumulative_req.venue.venue_admin
    print(' requester_email : ', requester_email)

    if not requester_email:
        print("Requester email not found.")
        return

    # Email content
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = requester_email  # Consider changing to venue in-charge email if needed
    msg['Subject'] = "Venue Booking Approved ✅"

    # Handle missing data with defaults
    full_name = req.full_name or "User"
    organization = req.organization_name or "N/A"
    event_type = req.event_type or "N/A"
    guest_count = req.guest_count or "N/A"
    additional_info = req.additional_info or "N/A"
    event_details = req.event_details or "N/A"
    purpose = req.purpose or "N/A"
    start_date = cumulative_req.start_date or "N/A"
    weekdays = cumulative_req.weekdays or "N/A"
    time = req.time or "N/A"
    duration = req.duration or "N/A"
    num_weeks = cumulative_req.num_weeks or "N/A"
    special_requirements = req.special_requirements or "None"
    venue_name = req.venue.venue_name if hasattr(req, 'venue') else "Unknown Venue"
    booking_id = req.cumulative_request_id

    body = f"""
Dear Venue In-charge,

Please be informed that a new venue booking request has been approved and requires your attention for further arrangements.

Here are the details and requirements of the booking:

📌 **Booking ID:** {booking_id}
- Requester Name: {full_name}
- Organization: {organization}
- Event Type: {event_type}
- Guest Count: {guest_count}
- Event Details: {event_details}
- Purpose: {purpose}
- Start Date: {start_date}
- Weekdays: {weekdays}
- Time: {time}:00 hrs
- Duration: {duration} hour(s)
- Number of Weeks: {num_weeks}
- Special Requirements: {special_requirements}
- Venue: {venue_name}

Please contact the requester for any clarifications or further arrangements needed to ensure all requirements for the venue are met.

Requester Contact:
- Email: {req.email}
- Phone (if available): {getattr(req, 'phone_number', 'N/A')}

Thank you for your cooperation.

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

    print('--------end : venue_admin_send_cumulative_booking_accepted_email-----------\n')






def send_cumulative_booking_accepted_email(req, cumulative_req, feedback_reason, feedback_comments):
    print('\n--------start : send_cumulative_booking_accepted_email-----------')
    print(req)
    # print(json.dumps(req, indent=4))  # Nicely formatted JSON-style print

    # Use email from request row directly
    requester_email = req.user.email
    print('requester_email : ', requester_email)

    if not requester_email:
        print("Requester email not found.")
        return

    # Email content
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = requester_email
    msg['Subject'] = "Venue Booking Approved ✅"

    print('ppjofsjd')

    # Handle missing data with defaults
    full_name = req.full_name or "User"
    organization = req.organization_name or "N/A"
    event_type = req.event_type or "N/A"
    guest_count = req.guest_count or "N/A"
    additional_info = req.additional_info or "N/A"
    event_details = req.event_details or "N/A"
    purpose = req.purpose or "N/A"
    # start_date = req.start_date or "N/A"
    start_date = req.date or "N/A"
    
    weekdays = cumulative_req.weekdays or "N/A"
    time = req.time or "N/A"
    duration = cumulative_req.duration or "N/A"
    num_weeks = cumulative_req.num_weeks or "N/A"
    special_requirements = req.special_requirements or "None"
    venue_name = req.venue.venue_name if hasattr(req, 'venue') else "Unknown Venue"
    booking_id = req.cumulative_request_id

    print('][]iuoueoiuf')

    body = f"""
Dear {full_name if full_name.strip() else 'Requester'},

Your venue booking request has been approved! 🎉

📌 **Booking Details**
- Booking ID: {booking_id}
- Organization: {organization}
- Event Type: {event_type}
- Guest Count: {guest_count}
- Event Details: {event_details}
- Purpose: {purpose}
- Start Date: {start_date}
- Weekdays: {weekdays}
- Time: {time}:00 hrs
- Duration: {duration} hour(s)
- Number of Weeks: {num_weeks}
- Special Requirements: {special_requirements}
- Venue: {venue_name}

💬 **Admin Feedback**
- Reason: {feedback_reason}
- Comments: {feedback_comments}

Please ensure to follow all venue rules and be present on time.

For any queries, contact the venue in-charge:
- Email : {req.venue.dept_incharge_email}
- Phone Number : {req.venue.dept_incharge_phone}

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

    print('--------end : send_booking_accepted_email-----------\n')




import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

def send_booking_rejected_email(req, full_msg):
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

    Reason for Rejection: {req.reasons}

    Message from the admin: {full_msg}  

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

def send_cumulative_booking_rejected_email(req,cumulative_req, full_msg):
    print('\n--------start : send_cumulative_booking_rejected_email-----------')

    requester_email = req.email  # From CumulativeRequest model

    if not requester_email:
        print("Requester email not found.")
        return

    # Email content
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = requester_email
    msg['Subject'] = "Venue Booking Rejected ❌"

    # Handle missing data with defaults
    full_name = req.full_name or "User"
    organization = req.organization_name or "N/A"
    event_type = req.event_type or "N/A"
    guest_count = req.guest_count or "N/A"
    event_details = req.event_details or "N/A"
    purpose = req.purpose or "N/A"
    start_date = cumulative_req.start_date or "N/A"
    weekdays = cumulative_req.weekdays or "N/A"
    time = req.time or "N/A"
    duration = cumulative_req.duration or "N/A"
    num_weeks = cumulative_req.num_weeks or "N/A"
    special_requirements = req.special_requirements or "None"
    venue_name = req.venue.venue_name if hasattr(req, 'venue') else "Unknown Venue"
    booking_id = req.cumulative_request_id

    body = f"""
Dear {full_name if full_name.strip() else 'Requester'},

We regret to inform you that your venue booking request has been rejected.

📌 **Request Details**
- Booking ID: {booking_id}
- Organization: {organization}
- Event Type: {event_type}
- Guest Count: {guest_count}
- Event Details: {event_details}
- Purpose: {purpose}
- Start Date: {start_date}
- Weekdays: {weekdays}
- Time: {time}:00 hrs
- Duration: {duration} hour(s)
- Number of Weeks: {num_weeks}
- Special Requirements: {special_requirements}
- Venue: {venue_name}

💬 **Admin Feedback**
{full_msg}

If you believe this was a mistake or you have further queries, feel free to reach out to the venue in-charge.

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

    print('--------end : send_cumulative_booking_rejected_email-----------\n')




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
        print('.........Ended in forward_request_to_alternate().......')
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
        



from datetime import datetime, date


def approve_request(request, request_id):
    print()
    print()
    print('-------in approve_request()-------')
    print('-------in approve_request()-------')
    print('-------in approve_request()-------')
    print('-------in approve_request()-------')
    print('-------in approve_request()-------')
    print()
    print()
    print()
    print()

    if request.method == "POST":
        print('in approve_request() ---ipsdcgjmfo-')
        # req = get_object_or_404(Request, request_id=request_id)
        # start_time = req.time
        # end_time = req.time + req.duration
        # Print all keys and values from the POST data
        for key, value in request.POST.items():
            print(f"{key}: {value}")

        print('ooooooooo')
        print(request.POST.items())
        print('pppppp')
        feedback_reason = request.POST.get('feedback_reason')
        feedback_comments = request.POST.get('feedback_comments')
        alternative_options = request.POST.get('alternative_options')

        print(feedback_reason)  # "Event appropriate for venue"
        print(feedback_comments)  # "dlsf"
        print(alternative_options)  # ""`
        print()
        print()
        print('pppppppjjj')


        admin_reason = request.POST.get('feedbackReason_Admin')
        admin_comments = request.POST.get('feedbackComments_Admin')

        print("additional_comments_Venueadmin",admin_comments)
        print("reason_for_approval",admin_reason)

        print('ijnsidhogwg')

        req = get_object_or_404(Request, request_id=request_id)

        # start_time = int(req.time.timestamp())  # Converts datetime to UNIX timestamp (integer)
        # end_time = start_time + int(req.duration)


        # start_time = datetime.combine(date.today(), req.time)  # Create a datetime object
        # start_time_seconds = int(start_time.timestamp())  # Convert to UNIX timestamp

        # end_time_seconds = start_time_seconds + int(req.duration)  # Assuming req.duration is in seconds

        user=CustomUser.objects.get(email=request.user)
        pending_requests = Request.objects.filter(
            venue=req.venue,
            date=req.date,
            status='pending',
            ).exclude(request_id=req.request_id)

        start_time = req.time
        end_time=start_time+req.duration

        conflicting_requests = []
        for existing in pending_requests:
            existing_start = existing.time
            existing_end = existing.time + existing.duration

            print('in conflict response for loop')
            print('-------------')
            print('-------------')
            print('-------------')
            print()
            print()
            
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
            "event_details": req.event_details,
            "additional_comments_Venueadmin":feedback_comments,
            "reason_for_approval":feedback_reason,       #dropdown
        }
        print()
        print('kkkkkkkkkkkk')
        print("additional_comments_Venueadmin",feedback_comments)
        print("reason_for_approval",feedback_reason)
        print()
        print()
        print()
        print()

        serializer = BookingSerializer(data=booking_data)

        if serializer.is_valid():
            with transaction.atomic():
                booking = serializer.save()  # Save Booking
                
                # ✅ Update request status to "approved" instead of deleting
                req.status = "approved"
                req.save(update_fields=["status"])

                print("✅ Booking saved successfully, request updated!")  # Debugging
                messages.success(request, "Booking approved and request status updated!")

                # send_booking_accepted_email(req)
                try:
                    send_booking_accepted_email(req , feedback_reason , feedback_comments)
                except Exception as e:
                    logger.error(f"Failed to send approval email for request {req.request_id}: {e}")
                print()
                print()

            return redirect('/venue_admin/requests')
        else:
            print("❌ Serializer errors:", serializer.errors)  # Debugging
            messages.error(request, "Error approving request.")

    return redirect('/venue_admin/requests')


def approve_cumulative_request(request, cumulative_request_id):
    print()
    print()
    print('-------in approve_cumulative_request()-------')
    print('-------in approve_cumulative_request()-------')
    print('-------in approve_cumulative_request()-------')
    print()
    print()

    if request.method == "POST":
        print('in approve_cumulative_request() --- POST received')
        
        # Print all keys and values from the POST data
        for key, value in request.POST.items():
            print(f"{key}: {value}")

        feedback_reason = request.POST.get('feedback_reason')
        feedback_comments = request.POST.get('feedback_comments')
        admin_reason = request.POST.get('feedbackReason_Admin')
        admin_comments = request.POST.get('feedbackComments_Admin')

        print("Feedback Reason:", feedback_reason)
        print("Feedback Comments:", feedback_comments)
        print("Admin Reason:", admin_reason)
        print("Admin Comments:", admin_comments)

        # Get the cumulative request
        cumulative_req = get_object_or_404(CumulativeRequest, cumulative_request_id=cumulative_request_id)
        user = CustomUser.objects.get(email=request.user)

        # Get all individual requests associated with this cumulative request
        individual_requests = Request.objects.filter(
            cumulative_request_id=cumulative_request_id,
            status='pending'  # Only approve pending requests
        )

        if not individual_requests.exists():
            messages.error(request, "No pending requests found for this cumulative booking.")
            return redirect('/venue_admin/requests')

        with transaction.atomic():
            # Process each individual request
            for req in individual_requests:
                # Check for conflicting requests for each individual date
                pending_requests = Request.objects.filter(
                    venue=req.venue,
                    date=req.date,
                    status='pending',
                    venue__department_incharge=user,
                ).exclude(request_id=req.request_id)

                start_time = req.time
                end_time = start_time + req.duration

                conflicting_requests = []
                for existing in pending_requests:
                    existing_start = existing.time
                    existing_end = existing.time + existing.duration

                    # Overlap conditions for slot-based conflict:
                    if (existing_end > start_time and existing_end < end_time) or (existing_start < end_time and existing_start > start_time):
                        conflicting_requests.append(existing)

                if conflicting_requests:
                    # Reject all conflicting requests
                    for conflict in conflicting_requests:
                        forward_request_to_alternate(conflict)

                # Prepare data for serializer
                booking_data = {
                    "booking_id": uuid.uuid4(),
                    "request": str(req.request_id),
                    "user": str(req.user.id),
                    "date": req.date,
                    "time": req.time,
                    "duration": req.duration,
                    "venue": str(req.venue.id),
                    "event_details": req.event_details,
                    "additional_comments_Venueadmin": feedback_comments,
                    "reason_for_approval": feedback_reason,
                }

                serializer = BookingSerializer(data=booking_data)

                if serializer.is_valid():
                    # Save booking
                    booking = serializer.save()
                    
                    # Update request status to "approved"
                    req.status = "approved"
                    req.save(update_fields=["status"])

                    # # Send approval email
                    # try:
                    #     # send_booking_accepted_email(req, feedback_reason, feedback_comments)
                    #     send_cumulative_booking_accepted_email(req, feedback_reason, feedback_comments)

                    # except Exception as e:
                    #     logger.error(f"Failed to send approval email for request {req.request_id}: {e}")
                else:
                    print("❌ Serializer errors:", serializer.errors)
                    messages.error(request, f"Error approving request {req.request_id}.")
                    continue  # Skip to next request if this one fails

            # Update the cumulative request status
            send_cumulative_booking_accepted_email(req, cumulative_req,feedback_reason, feedback_comments)
            venue_admin_send_cumulative_booking_accepted_email(req, cumulative_req,feedback_reason, feedback_comments)
            
            cumulative_req.status = "approved"
            cumulative_req.reasons = feedback_reason
            cumulative_req.save(update_fields=["status", "reasons"])

            messages.success(request, "All requests in the cumulative booking have been approved!")
            print("✅ All cumulative bookings processed successfully")

        return redirect('/venue_admin/cumulative_requests')

    return redirect('/venue_admin/cumulative_requests')



# def approved_bookings_view(request):
#     user_id = request.user.id
    
#     # ✅ Get the user (already logged in)
#     try:
#         user = CustomUser.objects.get(id=user_id)
#     except CustomUser.DoesNotExist:
#         return render(request, 'venue_admin/approved_bookings.html', {
#             'user': None,
#             'managed_venues': [],
#             'approved_bookings': []
#         })

#     # ✅ Get venues managed by the user
#     managed_venues = Venue.objects.filter(department_incharge=user)

#     # ✅ Get approved bookings for those venues
#     approved_bookings = Booking.objects.filter(
#         venue__in=managed_venues,
#         status='active'
#     ).select_related('user', 'venue')


#     # ✅ Pass data to context
#     context = {
#         'user': user,
#         'managed_venues': managed_venues,
#         'approved_bookings': approved_bookings
#     }

#     return render(request, 'venue_admin/approved_bookings.html', context)


def approved_bookings_view(request):
    user_id = request.user.id

    # ✅ Get the user (already logged in)
    try:
        user = CustomUser.objects.get(id=user_id)
    except CustomUser.DoesNotExist:
        return render(request, 'venue_admin/approved_bookings.html', {
            'user': None,
            'managed_venues': [],
            'approved_bookings_with_requests': []
        })

    # ✅ Get venues managed by the user
    managed_venues = Venue.objects.filter(department_incharge=user)

    # ✅ Get approved bookings for those venues
    approved_bookings = Booking.objects.filter(
        venue__in=managed_venues,
        status='active'
    ).select_related('user', 'venue', 'request')  # 🔥 Added 'request' here

    # ✅ Prepare combined list of (booking, request) pairs
    approved_bookings_with_requests = []
    for booking in approved_bookings:
        approved_bookings_with_requests.append({
            'booking': booking,
            'request': booking.request  # 🔥 Directly accessing the related Request
        })
    print('approved_bookings_with_requests : ', approved_bookings_with_requests)
    print('------')

    approved_bookings = approved_bookings_with_requests

    # ✅ Pass data to context
    context = {
        'user': user,
        'managed_venues': managed_venues,
        'approved_bookings': approved_bookings
    }

    return render(request, 'venue_admin/approved_bookings.html', context)
