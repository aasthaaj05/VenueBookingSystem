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
    BookingSerializer,
)
from gymkhana.models import Request, Booking, Venue, Rejection, RejectedBooking
from users.models import CustomUser
from django.views.decorators.csrf import csrf_exempt
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from django.conf import settings  # Import settings
from django.shortcuts import render, redirect
from django.contrib import messages
from gymkhana.models import Venue
from request_booking.models import Request
from django.contrib.auth import logout
from django.shortcuts import redirect
from django.shortcuts import get_object_or_404, redirect
from django.http import JsonResponse
import logging
from django.http import JsonResponse
from request_booking.models import CumulativeRequest
from request_booking.models import CumulativeRequest
from django.db.models import Q
import json
import smtplib
from django.utils.timezone import now
import ssl

logger = logging.getLogger(__name__)


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
    


def logout_view(request):
    # Clear the session data
    request.session.flush()
    
    # Logout the user
    logout(request)
    
    # Redirect to login or homepage
    return redirect('/users/login')  # Change 'login' to the actual login page name



def send_booking_rejected_email(req, full_msg):
    print('\n\n--------start : send_booking_rejected_email-----------')

    requester_email = req.user.email
    if not requester_email:
        print("Requester email not found.")
        return

    venue = req.venue
    incharge_email = venue.dept_incharge_email or "Not available"
    incharge_phone = venue.dept_incharge_phone or "Not available"

    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = requester_email
    msg['Subject'] = "Venue Booking Rejected ❌"

    body = f"""
Dear {req.user.name},

We regret to inform you that your venue booking request has been rejected.

Request Details:
- Request ID: {req.request_id}
- Venue: {venue.venue_name}
- Date: {req.date}
- Time: {req.time}
- Duration: {req.duration} hours
- Event Details: {req.event_details}

Reason for Rejection:
{full_msg}


Regards,  
COEP Venue Booking System
"""

    msg.attach(MIMEText(body, 'plain'))

    try:
        context = ssl.create_default_context()
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls(context=context)
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, requester_email, msg.as_string())
            print(f"Booking rejection email sent to {requester_email}")
    except Exception as e:
        print(f"Failed to send rejection email: {e}")

    print('-----end send_booking_rejected_email--------')



def reject_request(request, request_id):
    print("""Reject a request and store the reason in the rejection table.""")
    req = get_object_or_404(Request, request_id=request_id)
    print("Form data (POST):", request.POST)
    print("GET data (URL params):", request.GET)
    print("User:", request.user)
    print("Headers:", request.headers)



    if req.status != 'pending':
        return JsonResponse({"error": "Request is not in a pending state."}, status=400)
    reason = request.POST.get("feedback_reason", "")
    feedback_from_admin = request.POST.get("feedback_comments", "")
    alternate_venues_suggestion = request.POST.get("alternative_options", "")

    # Collect values safely
    rejection_reason = reason.strip()
    feedback = feedback_from_admin.strip()
    alternatives = alternate_venues_suggestion.strip()
    print('reason : ', reason)
    print('comments : ' , feedback_from_admin)
    print('alternatives : ' , alternate_venues_suggestion)
    print()
    print()

    # ✅ Construct message (optional formatting, you can change this)
    # full_msg = f"{feedback_from_admin}\n\nSuggested Alternatives:\n{alternate_venues_suggestion}".strip()


    # Dynamically construct full_msg
    full_msg_parts = []

    if rejection_reason:
        full_msg_parts.append(f"❌ Reason for Rejection: {rejection_reason}\n")

    if feedback:
        full_msg_parts.append(f"💬 Feedback from Admin: {feedback}\n")

    if alternatives:
        full_msg_parts.append(f"🏷️ Suggested Alternate Venues: {alternatives}\n")

    # Join all parts
    full_msg = "\n\n".join(full_msg_parts)



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

# def reject_cumulative_request(request, cumulative_request_id):
#     print("-------in reject_cumulative_request()-------")

#     if request.method == "POST":
#         print('POST data received in reject_cumulative_request():')
#         for key, value in request.POST.items():
#             print(f"{key}: {value}")

#         reason = request.POST.get("feedback_reason", "")
#         feedback_from_admin = request.POST.get("feedback_comments", "")
#         alternate_venues_suggestion = request.POST.get("alternative_options", "")

#         print("Reason:", reason)
#         print("Admin Feedback:", feedback_from_admin)
#         print("Alternatives:", alternate_venues_suggestion)

#         cumulative_req = get_object_or_404(CumulativeRequest, cumulative_request_id=cumulative_request_id)
#         individual_requests = Request.objects.filter(
#             cumulative_request_id=cumulative_request_id,
#             status='pending'  # Only reject pending requests
#         )

#         if not individual_requests.exists():
#             messages.error(request, "No pending requests found for this cumulative booking.")
#             return redirect('/venue_admin/cumulative_requests')

#         store_rejection_msg=""

#         with transaction.atomic():
#             for req in individual_requests:
#                 req.status = 'rejected'
#                 req.reasons = reason
#                 req.save(update_fields=["status", "reasons"])

#                 rejection = Rejection.objects.create(
#                     request=req,
#                     user=req.user,
#                     reason=reason,
#                     msg=f"{feedback_from_admin}\n\nSuggested Alternatives:\n{alternate_venues_suggestion}".strip(),
#                     feedback_from_admin=feedback_from_admin,
#                     alternate_venues_suggestion=alternate_venues_suggestion,
#                 )
#                 store_rejection_msg = rejection.msg

#                 # Send rejection email

#             cumulative_req.status = 'rejected'
#             cumulative_req.reasons = reason
#             cumulative_req.save(update_fields=["status", "reasons"])

#             send_cumulative_booking_rejected_email(req, cumulative_req,store_rejection_msg)

#             messages.success(request, "Cumulative booking and all its requests have been rejected.")
#             print("✅ Cumulative booking rejected successfully")

#         return redirect('/venue_admin/cumulative_requests')

#     return redirect('/venue_admin/cumulative_requests')


def reject_cumulative_request(request, cumulative_request_id):
    print("-------in reject_cumulative_request()-------")

    if request.method == "POST":
        print('POST data received in reject_cumulative_request():')
        for key, value in request.POST.items():
            print(f"{key}: {value}")

         # Debug: Print all POST data
        print('\n--- POST Data ---')
        for key, value in request.POST.items():
            print(f"{key}: {value}")

        reason = request.POST.get("feedbackReason_Admin", "")
        feedback_from_admin = request.POST.get("feedbackComments_Admin", "")
        alternate_venues_suggestion = request.POST.get("alternativeOptions", "")  # Make sure this matches your HTML

        # Get feedback data
        # feedback_reason = request.POST.get('feedbackReason_Admin', 'No reason provided')
        feedback_reason = request.POST.get('feedback_reason', 'No reason provided')
        cumulative_req_feedback_reason = feedback_reason
        # feedback_comments
        # feedback_comments = request.POST.get('feedbackComments_Admin', 'No comments')
        feedback_comments = request.POST.get('feedback_comments', 'No comments')
        cumulative_req_feedback_comments = feedback_comments
        alternative_options = request.POST.get('alternative_options', 'No alternatives suggested')
        cumulative_req_alternative_options = alternative_options

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

                
                print("Reason:", reason)
                print("Feedback from admin:", feedback_from_admin)
                print("Alternate venues suggestion:", alternate_venues_suggestion)
                print("Combined message:", f"{feedback_from_admin}\n\nSuggested Alternatives:\n{alternate_venues_suggestion}".strip())


                rejection = Rejection.objects.create(
                    request=req,
                    user=req.user,
                    reason=reason,
                    msg=f"{feedback_from_admin}\n\nSuggested Alternatives:\n{alternate_venues_suggestion}".strip(),
                    feedback_from_admin=feedback_from_admin,
                    alternate_venues_suggestion=alternate_venues_suggestion,
                )
                store_rejection_msg = rejection.msg

                # Send rejection email

            cumulative_req.status = 'rejected'
            cumulative_req.reasons = reason
            cumulative_req.save(update_fields=["status", "reasons"])

            
            cumulative_req.reasons = feedback_reason
            print('cumulative_req_feedback_reason : ', cumulative_req_feedback_reason)
            print('cumulative_req_feedback_comments : ', cumulative_req_feedback_comments)
            cumulative_req.reason_to_reject = cumulative_req_feedback_reason
            cumulative_req.additional_comments = cumulative_req_feedback_comments
            cumulative_req.suggest_alternate_venues = cumulative_req_alternative_options
            cumulative_req.accept=0
            '''
            feedback_reason = request.POST.get('feedback_reason', 'No reason provided')
            cumulative_req_feedback_reason = feedback_reason
            # feedback_comments
            # feedback_comments = request.POST.get('feedbackComments_Admin', 'No comments')
            feedback_comments = request.POST.get('feedback_comments', 'No comments')
            cumulative_req_feedback_comments = feedback_comments
            alternative_options = request.POST.get('alternative_options', 'No alternatives suggested')
            cumulative_req_alternative_options = alternative_options
            '''
            cumulative_req.save()  # Save all changes including feedback details

            send_cumulative_booking_rejected_email(req, cumulative_req, None)

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
                'time': req.time,  # Format time as HH:00
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
    return render(request, 'venue_admin/venue_admin_get_pending_requests.html', context)

def float_to_time_str(t):
    t = float(t)  # Convert string like '9.0' or '13.5' to float
    hours = int(t)
    minutes = int(round((t - hours) * 60))
    return f"{hours}:{minutes:02d}"


# def clean_multiline(text):
#     return text.replace('\n', '\\n').replace('\r', '').strip() if text else 'N/A'

def clean_multiline(text):
    return text.replace('\n', ' ').replace('\r', '').strip() if text else 'N/A'



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
            'time': float_to_time_str(cr.time),
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
            'event_details': clean_multiline(cr.event_details) if cr.event_details else 'N/A',
            'status': cr.status,
            'reasons': cr.reasons if cr.status == 'rejected' else None,
            'purpose': clean_multiline(cr.purpose) if cr.purpose else 'N/A',
            # 'additional_info': cr.additional_info,
            'additional_info': clean_multiline(individual_requests.first().additional_info) if individual_requests.exists() else 'N/A',
            'special_requirements': clean_multiline(cr.special_requirements),
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


def send_booking_accepted_email(req, feedback_reason, feedback_comments):
    print('\n\n--------start : send_booking_accepted_email-----------')
    
    # Get requester's email
    requester_email = req.user.email
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
        # Create SSL context
        context = ssl.create_default_context()
        
        print('Connecting to Outlook SMTP server...')
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            print(f'Connected to {smtp_server}:{smtp_port}')
            
            # Enable STARTTLS
            server.starttls(context=context)
            print('STARTTLS enabled')
            
            print('sender_email : ', sender_email)
            print('Attempting login...')
            server.login(sender_email, sender_password)
            print('Login successful!')
            
            # Send the email
            text = msg.as_string()
            server.sendmail(sender_email, requester_email, text)
            print(f"Booking approval email sent to {requester_email}")
            
    except smtplib.SMTPAuthenticationError as e:
        print(f"Authentication failed: {e}")
        print("Possible solutions:")
        print("1. Check if your Outlook password is correct")
        print("2. If 2FA is enabled, you may need an App Password")
        print("3. Check if 'Less secure app access' needs to be enabled (if applicable)")
        print("4. Verify that SMTP access is allowed for your account")
        
    except smtplib.SMTPConnectError as e:
        print(f"Failed to connect to SMTP server: {e}")
        print("Check your internet connection and firewall settings")
        
    except smtplib.SMTPException as e:
        print(f"SMTP error occurred: {e}")
        
    except Exception as e:
        print(f"Failed to send email: {e}")
        
    finally:
        print('-----end send_booking_accepted_email--------')
    
    # Call new function to notify the in-charge
    send_booking_accepted_email_to_incharge(req)
    print('\n\n')

def venue_admin_send_cumulative_booking_accepted_email(req, cumulative_req,feedback_reason, feedback_comments):
    print('\n--------start : venue_admin_send_cumulative_booking_accepted_email-----------')
    print(req)
    # print(json.dumps(req, indent=4))  # Nicely formatted JSON-style print

    # Use email from request row directly
    requester_email = cumulative_req.venue.dept_incharge_email
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

    #  Process weekdays to show day names and remove duplicates
    weekday_names = []
    if hasattr(cumulative_req, 'weekdays') and cumulative_req.weekdays:
        weekday_map = {
            0: "Monday",
            1: "Tuesday",
            2: "Wednesday",
            3: "Thursday",
            4: "Friday",
            5: "Saturday",
            6: "Sunday"
        }
        
        # Convert to list if it's not already (assuming it might be a string or other format)
        weekdays_data = cumulative_req.weekdays
        if isinstance(weekdays_data, str):
            # If it's a string like "0,0,2,2,3,3", split and convert to integers
            weekdays_list = [int(day) for day in weekdays_data.split(',')]
        elif isinstance(weekdays_data, (list, tuple)):
            weekdays_list = [int(day) for day in weekdays_data]
        else:
            weekdays_list = []
        
        # Get unique sorted weekday numbers and map to names
        unique_weekdays = sorted(set(weekdays_list))
        weekday_names = [weekday_map.get(day, "Unknown") for day in unique_weekdays]
    
    weekdays_display = ", ".join(weekday_names) if weekday_names else "N/A"

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
- Weekdays: {weekdays_display}
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

    #  Process weekdays to show day names and remove duplicates
    weekday_names = []
    if hasattr(cumulative_req, 'weekdays') and cumulative_req.weekdays:
        weekday_map = {
            0: "Monday",
            1: "Tuesday",
            2: "Wednesday",
            3: "Thursday",
            4: "Friday",
            5: "Saturday",
            6: "Sunday"
        }
        
        # Convert to list if it's not already (assuming it might be a string or other format)
        weekdays_data = cumulative_req.weekdays
        if isinstance(weekdays_data, str):
            # If it's a string like "0,0,2,2,3,3", split and convert to integers
            weekdays_list = [int(day) for day in weekdays_data.split(',')]
        elif isinstance(weekdays_data, (list, tuple)):
            weekdays_list = [int(day) for day in weekdays_data]
        else:
            weekdays_list = []
        
        # Get unique sorted weekday numbers and map to names
        unique_weekdays = sorted(set(weekdays_list))
        weekday_names = [weekday_map.get(day, "Unknown") for day in unique_weekdays]
    
    weekdays_display = ", ".join(weekday_names) if weekday_names else "N/A"

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
- Weekdays: {weekdays_display}
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


# def send_booking_rejected_email(req, full_msg):
#     print()
#     print()
#     print('--------start : send_booking_rejected_email-----------')
#     requester_email = req.user.email  # Get requester's email
#     print('requester_email : ', requester_email)

#     if not requester_email:
#         print("Requester email not found.")
#         return

#     # Email content
#     msg = MIMEMultipart()
#     msg['From'] = sender_email
#     msg['To'] = requester_email
#     msg['Subject'] = "Venue Booking Rejected ❌"

#     body = f"""
#     Dear {req.user.name},

#     We regret to inform you that your venue booking request has been rejected due to scheduling conflicts.  

#     Request Details:
#     - Booking ID: {req.request_id}
#     - Venue: {req.venue.venue_name}
#     - Date: {req.date}
#     - Time: {req.time}:00
#     - Duration: {req.duration} hours
#     - Event Details: {req.event_details}

#     - Reason for Rejection: {req.reasons}
#     - Message from the admin: {full_msg}  

#     What you can do next?
#     - Try booking a different venue.  
#     - Choose an alternative date/time.  
#     - Contact the venue in-charge for further assistance.

#     We apologize for the inconvenience. Feel free to reach out for any queries.

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

#         print(f"Booking rejection email sent to {requester_email}")
#     except Exception as e:
#         print(f"Failed to send email: {e}")

#     print('-----end send_booking_rejected_email--------')
#     print()
#     print()

# def send_cumulative_booking_rejected_email(req,cumulative_req, full_msg):
#     print('\n--------start : send_cumulative_booking_rejected_email-----------')

#     requester_email = req.email  # From CumulativeRequest model

#     if not requester_email:
#         print("Requester email not found.")
#         return

#     # Email content
#     msg = MIMEMultipart()
#     msg['From'] = sender_email
#     msg['To'] = requester_email
#     msg['Subject'] = "Venue Booking Rejected ❌"

#     # Handle missing data with defaults
#     full_name = req.full_name or "User"
#     organization = req.organization_name or "N/A"
#     event_type = req.event_type or "N/A"
#     guest_count = req.guest_count or "N/A"
#     event_details = req.event_details or "N/A"
#     purpose = req.purpose or "N/A"
#     start_date = cumulative_req.start_date or "N/A"
#     weekdays = cumulative_req.weekdays or "N/A"
#     time = req.time or "N/A"
#     duration = cumulative_req.duration or "N/A"
#     num_weeks = cumulative_req.num_weeks or "N/A"
#     special_requirements = req.special_requirements or "None"
#     venue_name = req.venue.venue_name if hasattr(req, 'venue') else "Unknown Venue"
#     booking_id = req.cumulative_request_id
#     reason_to_reject = cumulative_req.reason_to_reject or "N/A"
#     additional_comments = cumulative_req.additional_comments or "N/A"
#     suggest_alternate_venues= cumulative_req.suggest_alternate_venues or "N/A"

#     body = f"""
# Dear {full_name if full_name.strip() else 'Requester'},

# We regret to inform you that your venue booking request has been rejected.

# 📌 **Request Details**
# - Booking ID: {booking_id}
# - Organization: {organization}
# - Event Type: {event_type}
# - Guest Count: {guest_count}
# - Event Details: {event_details}
# - Purpose: {purpose}
# - Start Date: {start_date}
# - Weekdays: {weekdays}
# - Time: {time}:00 hrs
# - Duration: {duration} hour(s)
# - Number of Weeks: {num_weeks}
# - Special Requirements: {special_requirements}
# - Venue: {venue_name}

# 💬 **Admin Feedback**
# - Reason to reject : {reason_to_reject}
# - Additional Comments : {additional_comments}
# - Suggested Venue : {suggest_alternate_venues}

# If you believe this was a mistake or you have further queries, feel free to reach out to the venue in-charge.

# Regards,  
# COEP Venue Booking System
#     """

#     msg.attach(MIMEText(body, 'plain'))

#     # Send email
#     try:
#         with smtplib.SMTP(smtp_server, smtp_port) as server:
#             server.starttls()
#             server.login(sender_email, sender_password)
#             server.send_message(msg)
#         print(f"Booking rejection email sent to {requester_email}")
#     except Exception as e:
#         print(f"Failed to send email: {e}")

#     print('--------end : send_cumulative_booking_rejected_email-----------\n')



from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib

import calendar

def format_weekdays(weekdays_str):
    try:
        # Convert to set of integers to remove duplicates, then sort
        weekday_nums = sorted(set(int(day) for day in weekdays_str.split(',') if day.strip().isdigit()))
        # Convert to weekday names (0=Monday, 6=Sunday)
        weekday_names = [calendar.day_name[day % 7] for day in weekday_nums]
        return ', '.join(weekday_names)
    except Exception as e:
        print(f"Error formatting weekdays: {e}")
        return weekdays_str  # fallback to raw if anything goes wrong


def send_cumulative_booking_rejected_email(req, cumulative_req, full_msg):
    print('\n--------start : send_cumulative_booking_rejected_email-----------')
    print('\n--------start : send_cumulative_booking_rejected_email-----------')
    print('\n--------start : send_cumulative_booking_rejected_email-----------')
    print('\n--------start : send_cumulative_booking_rejected_email-----------')
    print('\n--------start : send_cumulative_booking_rejected_email-----------')

    requester_email = cumulative_req.email or req.email  # fallback  # From CumulativeRequest model

    if not requester_email:
        print("Requester email not found.")
        return

    # Email content
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = requester_email
    msg['Subject'] = "Venue Booking Rejected ❌"

    # # Handle missing data with defaults
    # full_name = req.full_name or "User"
    # organization = req.organization_name or "N/A"
    # event_type = req.event_type or "N/A"
    # guest_count = req.guest_count or "N/A"
    # event_details = req.event_details or "N/A"
    # purpose = req.purpose or "N/A"
    # start_date = cumulative_req.start_date or "N/A"
    # weekdays = cumulative_req.weekdays or "N/A"
    # time = req.time or "N/A"
    # duration = cumulative_req.duration or "N/A"
    # num_weeks = cumulative_req.num_weeks or "N/A"
    # special_requirements = req.special_requirements or "None"
    # venue_name = req.venue.venue_name if hasattr(req, 'venue') else "Unknown Venue"
    # booking_id = req.cumulative_request_id
    # reason_to_reject = cumulative_req.reason_to_reject or "N/A"
    # additional_comments = cumulative_req.additional_comments or "N/A"
    # suggest_alternate_venues = cumulative_req.suggest_alternate_venues or "N/A"

    # Handle missing data with defaults
    full_name = req.full_name or cumulative_req.full_name or "User"
    print("Full Name:", full_name)

    organization = req.organization_name or cumulative_req.organization_name or "N/A"
    print("Organization:", organization)

    event_type = req.event_type or cumulative_req.event_type or "N/A"
    print("Event Type:", event_type)

    guest_count = req.guest_count or cumulative_req.guest_count or "N/A"
    print("Guest Count:", guest_count)

    event_details = req.event_details or cumulative_req.event_details or "N/A"
    print("Event Details:", event_details)

    purpose = req.purpose or cumulative_req.purpose or "N/A"
    print("Purpose:", purpose)

    start_date = cumulative_req.start_date or "N/A"
    print("Start Date:", start_date)

    # weekdays = cumulative_req.weekdays or "N/A"
    # print("Weekdays:", weekdays)
    raw_weekdays = cumulative_req.weekdays or "N/A"
    weekdays = format_weekdays(raw_weekdays)


    time = req.time or "N/A"
    print("Time:", time)

    duration = cumulative_req.duration or "N/A"
    print("Duration:", duration)

    num_weeks = cumulative_req.num_weeks or "N/A"
    print("Number of Weeks:", num_weeks)

    special_requirements = req.special_requirements or "None"
    print("Special Requirements:", special_requirements)

    venue_name = req.venue.venue_name if hasattr(req, 'venue') else "Unknown Venue"
    print("Venue Name:", venue_name)

    booking_id = req.cumulative_request_id
    print("Booking ID:", booking_id)

    reason_to_reject = cumulative_req.reason_to_reject or "N/A"
    print("Reason to Reject:", reason_to_reject)

    additional_comments = cumulative_req.additional_comments or "N/A"
    print("Additional Comments:", additional_comments)

    suggest_alternate_venues = cumulative_req.suggest_alternate_venues or "N/A"
    print("Suggest Alternate Venues:", suggest_alternate_venues)


    print('\n--------mid : send_cumulative_booking_rejected_email-----------')
    print('\n--------mid : send_cumulative_booking_rejected_email-----------')
    print('\n--------mid : send_cumulative_booking_rejected_email-----------')

    # Include full_msg only if it's not '2' and not None
    if full_msg and full_msg != '2':
        full_msg_section = f"\n📢 Message-\n{full_msg}\n\n"
    else:
        full_msg_section = "- Reason to reject : {reason_to_reject} \n" \
                       "- Additional Comments : {additional_comments} \n" \
                       "- Suggested Venue : {suggest_alternate_venues}\n\n".format(
        reason_to_reject=reason_to_reject,
        additional_comments=additional_comments,
        suggest_alternate_venues=suggest_alternate_venues
    )

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
{full_msg_section}
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
            server.ehlo()  # Identify yourself to the server
            server.starttls()  # Secure the connection
            server.ehlo()  # Re-identify yourself after TLS)
            server.login(sender_email, sender_password)
            server.send_message(msg)

        print(f"Forwarding email sent to {requester_email}")
    except Exception as e:
        print(f"Failed to send email: {e}")

    print("-------- End: send_request_forwarded_email --------\n")
    print()
    print()


# def forward_request_to_alternate(request):
#     if request.venue== request.alternate_venue_1 and request.alternate_venue_1 == request.alternate_venue_2:
#         # Update the original request status
#         request.status = 'forwarded'
#         request.save()
#         return None
        
    
#     if request.venue== request.alternate_venue_1:
#         request.alternate_venue_1 = request.alternate_venue_2



#     print('.........in forward_request_to_alternate().......')
#     if request.alternate_venue_1:
#         if request.alternate_venue_1==request.alternate_venue_2:
#             request.alternate_venue_2=None
        
#         # Create a new request based on the existing one
#         new_request = Request.objects.create(
#             user=request.user,
#             date=request.date,
#             time=request.time,
#             duration=request.duration,
#             venue=request.alternate_venue_1,
#             need=request.need,
#             alternate_venue_1=request.alternate_venue_2,
#             alternate_venue_2=None,
#             event_details=request.event_details,
#             status='pending',
#             reasons="Forwarded from another venue"
#         )
#         # Update the original request status
#         request.status = 'forwarded'
#         request.save()

#         # ✅ Send email to notify requester about forwarding
#         send_request_forwarded_email(request, new_request.venue)
#         print('.........Ended in forward_request_to_alternate().......')
#         return new_request
#     else:
#         request.status = 'rejected'
#         request.reasons = 'Slot is unavailable due to conflicting booking.'
#         request.save()
#         Rejection.objects.create(
#             request=request,
#             user=request.user,
#             reason='Slot is unavailable due to conflicting booking.',
#             msg='Booking conflict with another approved request.'
#         )
        

def approve_request(request, request_id):
    print('-------in approve_request()-------')

    if request.method == "POST":
        print('in approve_request() --- POST received')
        
        # Print all POST data for debugging
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

        req = get_object_or_404(Request, request_id=request_id)
        print(f"Processing request {req.request_id} for {req.venue.venue_name} on {req.date}")

        # Check for conflicts with both pending and approved requests
        potential_conflicts = Request.objects.filter(
            venue=req.venue,
            date=req.date,
        ).exclude(
            Q(status='rejected') | 
            Q(status='cancelled') | 
            Q(status='user-cancelled') |
            Q(status='forwarded') |
            Q(request_id=req.request_id)
        )

        start_time = float(req.time)
        end_time = float(start_time) + float(req.duration)
        print('start_time->',start_time)
        print('type(start_time)->',type(start_time))

        print('end_time->',end_time)
        print('type(end_time)->',type(end_time))
        print(f"Checking time slot: {start_time} to {end_time}")

        conflicting_requests = []
        for existing in potential_conflicts:
            existing_start = float(existing.time)
            existing_end = float(existing.time) + float(existing.duration)
            print(f"Comparing with request {existing.request_id} ({existing.status}): {existing_start}-{existing_end}")

            if not (existing_end <= start_time or existing_start >= end_time):
                print("🛑 CONFLICT DETECTED!")
                conflicting_requests.append(existing)

        if conflicting_requests:
            print(f"Found {len(conflicting_requests)} conflicting requests")
            for conflict in conflicting_requests:
                if conflict.cumulative_booking:
                    print(f"Processing cumulative conflict (ID: {conflict.cumulative_request_id})")
                    # Reject all requests in the conflicting cumulative set
                    conflict_individual_requests = Request.objects.filter(
                        cumulative_request_id=conflict.cumulative_request_id
                    )
                    conflict_individual_requests.update(status='rejected')
                    # Update the cumulative request
                    # CumulativeRequest.objects.filter(
                    #     cumulative_request_id=conflict.cumulative_request_id
                    # ).update(status='rejected')

                    CumulativeRequest.objects.filter(
                        cumulative_request_id=conflict.cumulative_request_id
                    ).update(
                        status='rejected',
                        reason_to_reject='scheduling conflict',
                        additional_comments='try for another venue'
                    )


                    
                    # send_cumulative_booking_rejected_email(conflict,conflict.cumulative_request_id,"scheduling conflict")
                    cumulative_obj = CumulativeRequest.objects.get(cumulative_request_id=conflict.cumulative_request_id)
                    send_cumulative_booking_rejected_email(conflict, cumulative_obj, "scheduling conflict")

                    
                else:
                    # print(f"Processing individual conflict (ID: {conflict.request_id})")
                    # forward_request_to_alternate(conflict)

                    print(f"Processing individual conflict (ID: {conflict.request_id})")
                    result = forward_request_to_alternate(conflict)

                    # If no alternate venue was found and request was rejected inside the function
                    if result is None:
                        try:
                            send_request_rejected_email(conflict)
                        except Exception as e:
                            logger.error(f"❌ Failed to send rejection email for request {conflict.request_id}: {e}")

        # Prepare booking data
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
            with transaction.atomic():
                booking = serializer.save()
                req.status = "approved"
                req.save(update_fields=["status"])
                print("✅ Booking approved successfully")
                
                try:
                    send_booking_accepted_email(req, feedback_reason, feedback_comments)
                except Exception as e:
                    logger.error(f"Failed to send approval email: {e}")
                
                messages.success(request, "Booking approved successfully!")
            return redirect('/venue_admin/requests')
        else:
            print("❌ Serializer errors:", serializer.errors)
            messages.error(request, "Error approving request.")

    return redirect('/venue_admin/requests')



def is_venue_available(venue, date, start_time, duration):
    start_time = float(start_time)
    end_time = start_time + float(duration)

    potential_conflicts = Request.objects.filter(
        venue=venue,
        date=date
    ).exclude(
        Q(status='rejected') |
        Q(status='cancelled') |
        Q(status='user-cancelled') |
        Q(status='forwarded') |
        Q(status='waiting_for_approval') | 
        Q(status='pending')

    )

    for existing in potential_conflicts:
        existing_start = float(existing.time)
        existing_end = existing_start + float(existing.duration)

        if not (existing_end <= start_time or existing_start >= end_time):
            return False  # Conflict detected
    return True  # No conflicts






# def forward_request_to_alternate(request):
#     print(f"Forwarding request {request.request_id} to alternate venue")
    
#     # Check if we have alternate venues to try
#     if not request.alternate_venue_1 and not request.alternate_venue_2:
#         print("No alternate venues available - rejecting request")
#         request.status = 'rejected'
#         request.rejection_reason = 'No available alternate venues'
#         request.save()
#         return None

#     # Determine which alternate venue to try first
#     if request.alternate_venue_1 and request.alternate_venue_1 != request.venue:
#         new_venue = request.alternate_venue_1
#         next_alternate = request.alternate_venue_2
#     elif request.alternate_venue_2 and request.alternate_venue_2 != request.venue:
#         new_venue = request.alternate_venue_2
#         next_alternate = None
#     else:
#         print("No valid alternate venues - rejecting request")
#         request.status = 'rejected'
#         request.rejection_reason = 'No available alternate venues'
#         request.save()
#         return None

#     print(f"Creating new request for venue {new_venue.venue_name}")
    
#     # Create new forwarded request
#     new_request = Request.objects.create(
#         user=request.user,
#         date=request.date,
#         time=request.time,
#         duration=request.duration,
#         venue=new_venue,
#         need=request.need,
#         alternate_venue_1=next_alternate,
#         alternate_venue_2=None,
#         event_details=request.event_details,
#         status='pending',
#         reasons="Forwarded from another venue",
#         cumulative_booking=request.cumulative_booking,
#         cumulative_request_id=request.cumulative_request_id
#     )

#     # Update original request
#     request.status = 'forwarded'
#     request.save()

#     try:
#         send_request_forwarded_email(request, new_venue)
#     except Exception as e:
#         logger.error(f"Failed to send forwarding email: {e}")

#     return new_request




# def forward_request_to_alternate(request):
#     print(f"Forwarding request {request.request_id} to alternate venue")
    
#     alternate_venues = [v for v in [request.alternate_venue_1, request.alternate_venue_2] if v and v != request.venue]

#     for new_venue in alternate_venues:
#         print(f"Checking availability for alternate venue: {new_venue.venue_name}")
#         if is_venue_available(new_venue, request.date, request.time, request.duration):
#             print(f"✅ Alternate venue {new_venue.venue_name} is available. Forwarding request.")
            
#             # Create new forwarded request
#             new_request = Request.objects.create(
#                 user=request.user,
#                 date=request.date,
#                 time=request.time,
#                 duration=request.duration,
#                 venue=new_venue,
#                 need=request.need,
#                 alternate_venue_1=None,  # Don't cascade further alternates
#                 alternate_venue_2=None,
#                 event_details=request.event_details,
#                 status='pending',
#                 reasons="Forwarded from another venue",
#                 cumulative_booking=request.cumulative_booking,
#                 cumulative_request_id=request.cumulative_request_id
#             )

#             # Mark original request as forwarded
#             request.status = 'forwarded'
#             request.save()

#             try:
#                 send_request_forwarded_email(request, new_venue)
#             except Exception as e:
#                 logger.error(f"Failed to send forwarding email: {e}")

#             return new_request
#         else:
#             print(f"❌ Alternate venue {new_venue.venue_name} is NOT available.")

#     # No alternates available or all were conflicting
#     print("No alternate venues are available - rejecting request")
    
#     request.status = 'rejected'
#     request.rejection_reason = 'No available alternate venues'
#     request.save()
#     return None



def forward_request_to_alternate(request):
    print(f"Forwarding request {request.request_id} to alternate venue")

    alternate_venues = [v for v in [request.alternate_venue_1, request.alternate_venue_2] if v and v != request.venue]

    for new_venue in alternate_venues:
        print(f"Checking availability for alternate venue: {new_venue.venue_name}")
        
        if is_venue_available(new_venue, request.date, request.time, request.duration):
            print(f"✅ Alternate venue {new_venue.venue_name} is available. Updating request in-place.")

            # Update original request instead of creating a new one
            request.reasons = "Forwarded from another venue"
            request.venue = new_venue
            request.status = "pending"

            # Shift alternate venues
            if request.alternate_venue_1 == new_venue:
                request.alternate_venue_1 = request.alternate_venue_2
                request.alternate_venue_2 = None
            elif request.alternate_venue_2 == new_venue:
                request.alternate_venue_2 = None

            request.save()

            # Send mail
            try:
                send_request_forwarded_email(request, new_venue)
            except Exception as e:
                logger.error(f"Failed to send forwarding email: {e}")

            return request  # Updated original request

        else:
            print(f"❌ Alternate venue {new_venue.venue_name} is NOT available.")

    # No alternate venues available
    print("No alternate venues are available - rejecting request")
    request.status = 'rejected'
    request.rejection_reason = 'No available alternate venues'
    request.save()
    return None







from datetime import datetime, date


# def approve_request(request, request_id):
#     print('-------in approve_request()-------')

#     if request.method == "POST":
#         print('in approve_request() ---ipsdcgjmfo-')
#         # req = get_object_or_404(Request, request_id=request_id)
#         # start_time = req.time
#         # end_time = req.time + req.duration
#         # Print all keys and values from the POST data
#         for key, value in request.POST.items():
#             print(f"{key}: {value}")

#         print(request.POST.items())
#         feedback_reason = request.POST.get('feedback_reason')
#         feedback_comments = request.POST.get('feedback_comments')
#         alternative_options = request.POST.get('alternative_options')

#         print(feedback_reason)  # "Event appropriate for venue"
#         print(feedback_comments)  # "dlsf"
#         print(alternative_options)  # ""`


#         admin_reason = request.POST.get('feedbackReason_Admin')
#         admin_comments = request.POST.get('feedbackComments_Admin')

#         print("additional_comments_Venueadmin",admin_comments)
#         print("reason_for_approval",admin_reason)


#         req = get_object_or_404(Request, request_id=request_id)

#         user=CustomUser.objects.get(email=request.user)
#         pending_requests = Request.objects.filter(
#             venue=req.venue,
#             date=req.date,
#             status='pending',
#             ).exclude(request_id=req.request_id)

#         start_time = req.time
#         end_time=start_time+req.duration

#         conflicting_requests = []
#         for existing in pending_requests:
#             existing_start = existing.time
#             existing_end = existing.time + existing.duration

#             print('in conflict response for loop')
#             print('-------------')
            
#             # ✅ Overlap conditions for slot-based conflict:
#             if not (existing_end <= start_time or existing_start >= end_time):
#                 conflicting_requests.append(existing)


#         if conflicting_requests:
#             # Reject all conflicting requests
#             for conflict in conflicting_requests:
#                 if conflict.cumulative_booking:  # No need for == '1' since it's a BooleanField
                    
#                     # Get the cumulative request using the cumulative_request_id
#                     cumulative_request = CumulativeRequest.objects.get(
#                         cumulative_request_id=conflict.cumulative_request_id
#                     )
#                     # Update the status to 'rejected'
#                     cumulative_request.status = 'rejected'
#                     cumulative_request.save()
#                 else:
#                     forward_request_to_alternate(conflict)



#         # Prepare data for serializer
#         booking_data = {
#             "booking_id": uuid.uuid4(),  # ✅ Ensure new UUID is assigned
#             "request": str(req.request_id),  # ✅ Directly pass request object (since it's a OneToOneField)
#             "user": str(req.user.id),
#             "date": req.date,
#             "time": req.time,
#             "duration": req.duration,
#             "venue": str(req.venue.id),
#             "event_details": req.event_details,
#             "additional_comments_Venueadmin":feedback_comments,
#             "reason_for_approval":feedback_reason,       #dropdown
#         }
#         print("additional_comments_Venueadmin",feedback_comments)
#         print("reason_for_approval",feedback_reason)

#         serializer = BookingSerializer(data=booking_data)

#         if serializer.is_valid():
#             with transaction.atomic():
#                 booking = serializer.save()  # Save Booking
                
#                 # ✅ Update request status to "approved" instead of deleting
#                 req.status = "approved"
#                 req.save(update_fields=["status"])

#                 print("✅ Booking saved successfully, request updated!")  # Debugging
#                 messages.success(request, "Booking approved and request status updated!")

#                 # send_booking_accepted_email(req)
#                 try:
#                     send_booking_accepted_email(req , feedback_reason , feedback_comments)
#                 except Exception as e:
#                     logger.error(f"Failed to send approval email for request {req.request_id}: {e}")

#             return redirect('/venue_admin/requests')
#         else:
#             print("❌ Serializer errors:", serializer.errors)  # Debugging
#             messages.error(request, "Error approving request.")

#     return redirect('/venue_admin/requests')


# def approve_cumulative_request(request, cumulative_request_id):
#     print('-------in approve_cumulative_request()-------')

#     if request.method == "POST":
#         print('in approve_cumulative_request() --- POST received')
        
#         # Print all keys and values from the POST data
#         for key, value in request.POST.items():
#             print(f"{key}: {value}")

#         feedback_reason = request.POST.get('feedback_reason')
#         feedback_comments = request.POST.get('feedback_comments')
#         admin_reason = request.POST.get('feedbackReason_Admin')
#         admin_comments = request.POST.get('feedbackComments_Admin')

#         print("Feedback Reason:", feedback_reason)
#         print("Feedback Comments:", feedback_comments)
#         print("Admin Reason:", admin_reason)
#         print("Admin Comments:", admin_comments)

#         # Get the cumulative request
#         cumulative_req = get_object_or_404(CumulativeRequest, cumulative_request_id=cumulative_request_id)
#         user = CustomUser.objects.get(email=request.user)

#         # Get all individual requests associated with this cumulative request
#         individual_requests = Request.objects.filter(
#             cumulative_request_id=cumulative_request_id,
#             status='pending'  # Only approve pending requests
#         )

#         if not individual_requests.exists():
#             messages.error(request, "No pending requests found for this cumulative booking.")
#             return redirect('/venue_admin/requests')

#         with transaction.atomic():
#             # Process each individual request
#             for req in individual_requests:
#                 # Check for conflicting requests for each individual date
#                 pending_requests = Request.objects.filter(
#                     venue=req.venue,
#                     date=req.date,
#                     status='pending',
                    
#                 ).exclude(request_id=req.request_id)

#                 print('pending_requests : ', pending_requests)

#                 start_time = req.time
#                 end_time = start_time + req.duration

#                 conflicting_requests = []
#                 for existing in pending_requests:
#                     existing_start = existing.time
#                     existing_end = existing.time + existing.duration

#                     # Overlap conditions for slot-based conflict:
#                     if (existing_end > start_time and existing_end < end_time) or (existing_start < end_time and existing_start > start_time):
#                         conflicting_requests.append(existing)

#                 print('')
#                 print('conflicting_requests : ', conflicting_requests)
#                 if conflicting_requests:
#                     # Reject all conflicting requests
#                     for conflict in conflicting_requests:
#                         if conflict.cumulative_booking:
#                             print('0980808089098')
#                             # Get the cumulative request using the cumulative_request_id
#                             cumulative_request = CumulativeRequest.objects.get(
#                                 cumulative_request_id=conflict.cumulative_request_id
#                             )
#                             print('ocjdsi9cusdoi')
#                             # Update the status to 'rejected'
#                             cumulative_request.status = 'rejected'
#                             cumulative_request.save()
#                         else:
#                             print('089098')
#                             forward_request_to_alternate(conflict)

#                 # Prepare data for serializer
#                 booking_data = {
#                     "booking_id": uuid.uuid4(),
#                     "request": str(req.request_id),
#                     "user": str(req.user.id),
#                     "date": req.date,
#                     "time": req.time,
#                     "duration": req.duration,
#                     "venue": str(req.venue.id),
#                     "event_details": req.event_details,
#                     "additional_comments_Venueadmin": feedback_comments,
#                     "reason_for_approval": feedback_reason,
#                 }

#                 serializer = BookingSerializer(data=booking_data)

#                 if serializer.is_valid():
#                     # Save booking
#                     booking = serializer.save()
                    
#                     # Update request status to "approved"
#                     req.status = "approved"
#                     req.save(update_fields=["status"])

#                     # # Send approval email
#                     # try:
#                     #     # send_booking_accepted_email(req, feedback_reason, feedback_comments)
#                     #     send_cumulative_booking_accepted_email(req, feedback_reason, feedback_comments)

#                     # except Exception as e:
#                     #     logger.error(f"Failed to send approval email for request {req.request_id}: {e}")
#                 else:
#                     print("❌ Serializer errors:", serializer.errors)
#                     messages.error(request, f"Error approving request {req.request_id}.")
#                     continue  # Skip to next request if this one fails

#             # Update the cumulative request status
#             send_cumulative_booking_accepted_email(req, cumulative_req,feedback_reason, feedback_comments)
#             venue_admin_send_cumulative_booking_accepted_email(req, cumulative_req,feedback_reason, feedback_comments)
            
#             cumulative_req.status = "approved"
#             cumulative_req.reasons = feedback_reason
#             cumulative_req.save(update_fields=["status", "reasons"])

#             messages.success(request, "All requests in the cumulative booking have been approved!")
#             print("✅ All cumulative bookings processed successfully")

#         return redirect('/venue_admin/cumulative_requests')

#     return redirect('/venue_admin/cumulative_requests')


# def approve_cumulative_request(request, cumulative_request_id):
#     print('\n\n===== START: approve_cumulative_request() =====')
#     print(f'Cumulative Request ID: {cumulative_request_id}')
#     print(f'Request method: {request.method}')

#     if request.method == "POST":
#         print('\n=== Processing POST request ===')
        
#         # Debug: Print all POST data
#         print('\n--- POST Data ---')
#         for key, value in request.POST.items():
#             print(f"{key}: {value}")

#         # Get feedback data
#         feedback_reason = request.POST.get('feedback_reason', 'No reason provided')
#         feedback_comments = request.POST.get('feedback_comments', 'No comments')
#         admin_reason = request.POST.get('feedbackReason_Admin', 'No admin reason')
#         admin_comments = request.POST.get('feedbackComments_Admin', 'No admin comments')

#         print('\n--- Feedback Data ---')
#         print(f"Feedback Reason: {feedback_reason}")
#         print(f"Feedback Comments: {feedback_comments}")
#         print(f"Admin Reason: {admin_reason}")
#         print(f"Admin Comments: {admin_comments}")

#         # Get the cumulative request
#         print('\n--- Fetching Cumulative Request ---')
#         try:
#             cumulative_req = get_object_or_404(CumulativeRequest, cumulative_request_id=cumulative_request_id)
#             print(f'Found CumulativeRequest: {cumulative_req}')
#             print(f'Status: {cumulative_req.status}')
#             print(f'User: {cumulative_req.user.email}')
#             print(f'Venue: {cumulative_req.venue.venue_name}')
#         except Exception as e:
#             print(f'❌ Error fetching cumulative request: {str(e)}')
#             messages.error(request, "Cumulative request not found.")
#             return redirect('/venue_admin/requests')

#         # Get all individual requests
#         print('\n--- Fetching Individual Requests ---')
#         individual_requests = Request.objects.filter(
#             cumulative_request_id=cumulative_request_id,
#             status='pending'
#         )
#         print(f'Found {individual_requests.count()} pending individual requests')

#         if not individual_requests.exists():
#             print('❌ No pending requests found for this cumulative booking')
#             messages.error(request, "No pending requests found for this cumulative booking.")
#             return redirect('/venue_admin/requests')

#         with transaction.atomic():
#             print('\n=== Starting Transaction ===')
            
#             for req in individual_requests:
#                 print(f'\n--- Processing Request {req.request_id} ---')
#                 print(f'Date: {req.date}, Time: {req.time}, Duration: {req.duration} mins')
#                 print(f'Venue: {req.venue.venue_name}')
                
#                 # Calculate time slots
#                 start_time = req.time
#                 end_time = start_time + req.duration
#                 print(f'Time Slot: {start_time} to {end_time}')

#                 # Find potential conflicts
#                 print('\n--- Checking for Conflicts ---')
#                 conflicting_requests = Request.objects.filter(
#                     venue=req.venue,
#                     date=req.date,
#                 ).exclude(
#                     Q(status='rejected') | 
#                     Q(status='cancelled') | 
#                     Q(status='user-cancelled') |
#                     Q(request_id=req.request_id)
#                 )
#                 print(f'Found {conflicting_requests.count()} potential conflicting requests')

#                 actual_conflicts = []
#                 for existing in conflicting_requests:
#                     existing_start = existing.time
#                     existing_end = existing.time + existing.duration
#                     print(f'\nChecking conflict with request {existing.request_id}:')
#                     print(f'Existing slot: {existing_start} to {existing_end}')
#                     print(f'New slot:     {start_time} to {end_time}')

#                     # Check for time overlap
#                     if not (existing_end <= start_time or existing_start >= end_time):
#                         print('🛑 CONFLICT DETECTED!')
#                         actual_conflicts.append(existing)
#                     else:
#                         print('✅ No time conflict')

#                 print(f'\nFound {len(actual_conflicts)} actual conflicts')

#                 if actual_conflicts:
#                     print('\n--- Handling Conflicts ---')
#                     for conflict in actual_conflicts:
#                         if conflict.cumulative_booking:
#                             print(f'🔄 Processing cumulative conflict (ID: {conflict.cumulative_request_id})')
#                             # Reject all requests in the conflicting cumulative set
#                             conflict_individual_requests = Request.objects.filter(
#                                 cumulative_request_id=conflict.cumulative_request_id
#                             )
#                             print(f'Found {conflict_individual_requests.count()} requests in conflicting cumulative set')
#                             conflict_individual_requests.update(status='rejected')
#                             print('Updated all individual requests in conflicting cumulative set to "rejected"')
                            
#                             # Update the cumulative request
#                             CumulativeRequest.objects.filter(
#                                 cumulative_request_id=conflict.cumulative_request_id
#                             ).update(status='rejected')
#                             print('Updated conflicting cumulative request to "rejected"')
#                         else:
#                             print(f'🔄 Processing individual conflict (ID: {conflict.request_id})')
#                             conflict.status = 'rejected'
#                             conflict.save()
#                             print('Updated individual conflicting request to "rejected"')

#                 # Create booking
#                 print('\n--- Creating Booking ---')
#                 booking_data = {
#                     "booking_id": uuid.uuid4(),
#                     "request": str(req.request_id),
#                     "user": str(req.user.id),
#                     "date": req.date,
#                     "time": req.time,
#                     "duration": req.duration,
#                     "venue": str(req.venue.id),
#                     "event_details": req.event_details,
#                     "additional_comments_Venueadmin": feedback_comments,
#                     "reason_for_approval": feedback_reason,
#                 }
#                 print('Booking data prepared:')
#                 for k, v in booking_data.items():
#                     print(f'{k}: {v}')

#                 serializer = BookingSerializer(data=booking_data)
#                 if serializer.is_valid():
#                     print('✅ Booking data is valid')
#                     booking = serializer.save()
#                     print(f'Booking created with ID: {booking.booking_id}')
                    
#                     # Update request status
#                     req.status = "approved"
#                     req.save(update_fields=["status"])
#                     print('Request status updated to "approved"')
#                 else:
#                     print('❌ Serializer errors:', serializer.errors)
#                     messages.error(request, f"Error approving request {req.request_id}.")
#                     continue

#             # Finalize cumulative request
#             print('\n--- Finalizing Cumulative Request ---')
#             try:
#                 send_cumulative_booking_accepted_email(req, cumulative_req, feedback_reason, feedback_comments)
#                 venue_admin_send_cumulative_booking_accepted_email(req, cumulative_req, feedback_reason, feedback_comments)
#                 print('Notification emails sent')
#             except Exception as e:
#                 print(f'❌ Error sending emails: {str(e)}')

#             cumulative_req.status = "approved"
#             cumulative_req.reasons = feedback_reason
#             cumulative_req.save(update_fields=["status", "reasons"])
#             print(f'Cumulative request {cumulative_req.cumulative_request_id} approved')

#             messages.success(request, "All requests in the cumulative booking have been approved!")
#             print("\n===== OPERATION COMPLETED SUCCESSFULLY =====")

#         return redirect('/venue_admin/cumulative_requests')

#     print('\n===== END: Not a POST request =====')
#     return redirect('/venue_admin/cumulative_requests')

def send_request_rejected_email(req):
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = req.user.email
    msg['Subject'] = "Venue Booking Request Rejected ❌"

    body = f"""
    Dear {req.user.name},

    We regret to inform you that your venue booking request for {req.venue.venue_name} on {req.date} at {req.time}
    has been rejected due to scheduling conflicts and no alternate venues being available.

    Please try again with a different venue or date.

    Regards,  
    COEP Venue Booking System
    """
    msg.attach(MIMEText(body, 'plain'))

    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.send_message(msg)
        print(f"Rejection email sent to {req.user.email}")
    except Exception as e:
        print(f"Failed to send rejection email: {e}")



def approve_cumulative_request(request, cumulative_request_id):
    print('\n\n===== START: approve_cumulative_request() =====')
    print(f'Cumulative Request ID: {cumulative_request_id}')
    print(f'Request method: {request.method}')

    if request.method == "POST":
        print('\n=== Processing POST request ===')
        
        # Debug: Print all POST data
        print('\n--- POST Data ---')
        for key, value in request.POST.items():
            print(f"{key}: {value}")

        # Get feedback data
        # feedback_reason = request.POST.get('feedbackReason_Admin', 'No reason provided')
        feedback_reason = request.POST.get('feedback_reason', 'No reason provided')
        cumulative_req_feedback_reason = feedback_reason
        # feedback_comments
        # feedback_comments = request.POST.get('feedbackComments_Admin', 'No comments')
        feedback_comments = request.POST.get('feedback_comments', 'No comments')
        cumulative_req_feedback_comments = feedback_comments
        alternative_options = request.POST.get('alternativeOptions', 'No alternatives suggested')

        print('\n--- Feedback Data ---')
        print(f"Feedback Reason: {feedback_reason}")
        print(f"Feedback Comments: {feedback_comments}")
        print(f"Alternative Options: {alternative_options}")

        # Get the cumulative request
        print('\n--- Fetching Cumulative Request ---')
        try:
            cumulative_req = get_object_or_404(CumulativeRequest, cumulative_request_id=cumulative_request_id)
            print(f'Found CumulativeRequest: {cumulative_req}')
            print(f'Status: {cumulative_req.status}')
            print(f'User: {cumulative_req.user.email}')
            print(f'Venue: {cumulative_req.venue.venue_name}')
            
            # Store all feedback details in the cumulative request
            cumulative_req.reason_to_approve = feedback_reason
            cumulative_req.additional_comments = feedback_comments
            cumulative_req.alternative_options = alternative_options
            cumulative_req.accept = 1  # 1 for accept
            print('Stored all feedback details in cumulative request')
            
        except Exception as e:
            print(f'❌ Error fetching cumulative request: {str(e)}')
            messages.error(request, "Cumulative request not found.")
            return redirect('/venue_admin/requests')

        # Get all individual requests
        print('\n--- Fetching Individual Requests ---')
        individual_requests = Request.objects.filter(
            cumulative_request_id=cumulative_request_id,
            status='pending'
        )
        print(f'Found {individual_requests.count()} pending individual requests')

        if not individual_requests.exists():
            print('❌ No pending requests found for this cumulative booking')
            messages.error(request, "No pending requests found for this cumulative booking.")
            return redirect('/venue_admin/requests')

        with transaction.atomic():
            print('\n=== Starting Transaction ===')
            
            for req in individual_requests:
                print(f'\n--- Processing Request {req.request_id} ---')
                print(f'Date: {req.date}, Time: {req.time}, Duration: {req.duration} mins')
                print(f'Venue: {req.venue.venue_name}')
                
                # Calculate time slots
                start_time = float(req.time)
                end_time = float(start_time) + float(req.duration)
                print(f'Time Slot: {start_time} to {end_time}')

                # Find potential conflicts
                print('\n--- Checking for Conflicts ---')
                conflicting_requests = Request.objects.filter(
                    venue=req.venue,
                    date=req.date,
                ).exclude(
                    Q(status='rejected') | 
                    Q(status='cancelled') | 
                    Q(status='user-cancelled') |
                    Q(request_id=req.request_id)
                )
                print(f'Found {conflicting_requests.count()} potential conflicting requests')

                actual_conflicts = []
                for existing in conflicting_requests:
                    existing_start = float(existing.time)
                    existing_end = float(existing.time) + float(existing.duration)
                    print(f'\nChecking conflict with request {existing.request_id}:')
                    print(f'Existing slot: {existing_start} to {existing_end}')
                    print(f'New slot:     {start_time} to {end_time}')

                    # Check for time overlap
                    if not (existing_end <= start_time or existing_start >= end_time):
                        print('🛑 CONFLICT DETECTED!')
                        actual_conflicts.append(existing)
                    else:
                        print('✅ No time conflict')

                print(f'\nFound {len(actual_conflicts)} actual conflicts')

                if actual_conflicts:
                    print('\n--- Handling Conflicts ---')
                    for conflict in actual_conflicts:
                        if conflict.cumulative_booking:
                            print(f'🔄 Processing cumulative conflict (ID: {conflict.cumulative_request_id})')
                            # Reject all requests in the conflicting cumulative set
                            conflict_individual_requests = Request.objects.filter(
                                cumulative_request_id=conflict.cumulative_request_id
                            )
                            print(f'Found {conflict_individual_requests.count()} requests in conflicting cumulative set')
                            conflict_individual_requests.update(status='rejected')
                            # send_request_forwarded_email(conflict,None)
                            cumulative_obj = CumulativeRequest.objects.get(cumulative_request_id=conflict.cumulative_request_id)
                            send_cumulative_booking_rejected_email(conflict, cumulative_obj, "scheduling conflict")

                            print('Updated all individual requests in conflicting cumulative set to "rejected"')
                            
                            # Update the cumulative request
                            CumulativeRequest.objects.filter(
                                cumulative_request_id=conflict.cumulative_request_id
                            ).update(status='rejected')
                            print('Updated conflicting cumulative request to "rejected"')
                        else:
                            # print(f'🔄 Processing individual conflict (ID: {conflict.request_id})')
                            # send_request_forwarded_email(conflict,None)
                            # conflict.status = 'rejected'
                            # conflict.save()
                            # print('Updated individual conflicting request to "rejected"')
                            print(f'🔄 Processing individual conflict (ID: {conflict.request_id})')

                            # Try forwarding to an alternate venue
                            forwarded_request = forward_request_to_alternate(conflict)

                            if forwarded_request:
                                print(f"✅ Conflict resolved by forwarding to alternate venue (ID: {forwarded_request.request_id})")
                                # Email is already sent inside forward_request_to_alternate()
                            else:
                                print("❌ No alternate venue available. Rejecting request.")

                                conflict.status = 'rejected'
                                conflict.rejection_reason = 'Scheduling conflict'
                                conflict.save()

                                try:
                                    send_request_rejected_email(conflict)  # <-- a separate rejection email
                                except Exception as e:
                                    logger.error(f"Failed to send rejection email: {e}")

                                print('Updated individual conflicting request to "rejected"')

                # Create booking
                print('\n--- Creating Booking ---')
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
                print('Booking data prepared:')
                for k, v in booking_data.items():
                    print(f'{k}: {v}')

                serializer = BookingSerializer(data=booking_data)
                if serializer.is_valid():
                    print('✅ Booking data is valid')
                    booking = serializer.save()
                    print(f'Booking created with ID: {booking.booking_id}')
                    
                    # Update request status
                    req.status = "approved"
                    req.save(update_fields=["status"])
                    print('Request status updated to "approved"')
                else:
                    print('❌ Serializer errors:', serializer.errors)
                    messages.error(request, f"Error approving request {req.request_id}.")
                    continue

            # Finalize cumulative request
            print('\n--- Finalizing Cumulative Request ---')
            try:
                send_cumulative_booking_accepted_email(req, cumulative_req, feedback_reason, feedback_comments)
                venue_admin_send_cumulative_booking_accepted_email(req, cumulative_req, feedback_reason, feedback_comments)
                print('Notification emails sent')
            except Exception as e:
                print(f'❌ Error sending emails: {str(e)}')

            cumulative_req.status = "approved"
            cumulative_req.reasons = feedback_reason
            print('cumulative_req_feedback_reason : ', cumulative_req_feedback_reason)
            print('cumulative_req_feedback_comments : ', cumulative_req_feedback_comments)
            cumulative_req.reason_to_approve = cumulative_req_feedback_reason
            cumulative_req.additional_comments = cumulative_req_feedback_comments
            cumulative_req.accept=1
            cumulative_req.save()  # Save all changes including feedback details
            print(f'Cumulative request {cumulative_req.cumulative_request_id} approved with all details')

            messages.success(request, "All requests in the cumulative booking have been approved!")
            print("\n===== OPERATION COMPLETED SUCCESSFULLY =====")

        return redirect('/venue_admin/cumulative_requests')

    print('\n===== END: Not a POST request =====')
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
#             'approved_bookings_with_requests': []
#         })

#     # ✅ Get venues managed by the user
#     managed_venues = Venue.objects.filter(venue_admin=user)

#     # ✅ Get approved bookings for those venues
#     approved_bookings = Booking.objects.filter(
#         venue__in=managed_venues,
#         status='active'
#     ).select_related('user', 'venue', 'request')  # 🔥 Added 'request' here

#     # ✅ Prepare combined list of (booking, request) pairs
#     approved_bookings_with_requests = []
#     for booking in approved_bookings:
#         approved_bookings_with_requests.append({
#             'booking': booking,
#             'request': booking.request  # 🔥 Directly accessing the related Request
#         })
#     print('approved_bookings_with_requests : ', approved_bookings_with_requests)
#     print('------')

#     approved_bookings = approved_bookings_with_requests

#     # ✅ Pass data to context
#     context = {
#         'user': user,
#         'managed_venues': managed_venues,
#         'approved_bookings': approved_bookings
#     }

#     return render(request, 'venue_admin/approved_bookings.html', context)



# def approved_bookings_view(request):
#     print('in approved_bookings_view()')
#     user = request.user

#     # ✅ Early exit if user is not authenticated or not found
#     if not user.is_authenticated:
#         print('user is not authenticated')
#         return render(request, 'venue_admin/approved_bookings.html', {
#             'user': None,
#             'managed_venues': [],
#             'approved_bookings': []
#         })

#     # ✅ Get venues managed by the user
#     # managed_venues = Venue.objects.filter(venue_admin=user)
#     # ✅ Get venues managed by the user (or all venues if role is gymkhana)
#     managed_venues=[]
#     # Normalize the role for comparison
#     user_role = user.role.strip().lower()

#     # ✅ If user is venue_admin (by role), show all venues; else filter by user.email
#     if user_role == 'venue_admin':
#         managed_venues = Venue.objects.all()    

#     # print('managed_venues ->', managed_venues)

#     # print('managed_venues->',managed_venues)

#     # ✅ If no venues managed, avoid unnecessary DB hits
#     if not managed_venues.exists():
#         return render(request, 'venue_admin/approved_bookings.html', {
#             'user': user,
#             'managed_venues': [],
#             'approved_bookings': []
#         })

#     # ✅ Get approved bookings with eager loading of related objects
#     approved_bookings = Booking.objects.filter(
#         venue__in=managed_venues,
#         status='active'
#     ).select_related('user', 'venue', 'request')

#     # ✅ Prepare combined list of (booking, request) dictionaries
#     approved_bookings_with_requests = []
#     for booking in approved_bookings:
#         if booking.request:  # safeguard in case of data issues
#             approved_bookings_with_requests.append({
#                 'booking': booking,
#                 'request': booking.request
#             })

#     # ✅ Optional debug print (remove in production)
#     print('approved_bookings_with_requests:', approved_bookings_with_requests)

#     # ✅ Prepare context for template rendering
#     context = {
#         'user': user,
#         'managed_venues': managed_venues,
#         'approved_bookings': approved_bookings_with_requests
#     }

#     return render(request, 'venue_admin/approved_bookings.html', context)


from collections import defaultdict

def approved_bookings_view(request):
    print('in approved_bookings_view()')
    user = request.user

    if not user.is_authenticated:
        print('user is not authenticated')
        return render(request, 'venue_admin/approved_bookings.html', {
            'user': None,
            'managed_venues': [],
            'approved_bookings': []
        })

    # ✅ Get venues managed by the user (or all venues if role is venue_admin)
    user_role = user.role.strip().lower()
    if user_role == 'venue_admin':
        managed_venues = Venue.objects.all()
    else:
        managed_venues = Venue.objects.filter(venue_admin=user.email)

    if not managed_venues.exists():
        return render(request, 'venue_admin/approved_bookings.html', {
            'user': user,
            'managed_venues': [],
            'approved_bookings': []
        })

    # ✅ Fetch all approved bookings
    approved_bookings = Booking.objects.filter(
        venue__in=managed_venues,
        status='active',
        request__cumulative_request_id__isnull=True  # <-- this line filters out cumulative requests
    ).select_related('user', 'venue', 'request')

    # Prepare the list to pass to template
    filtered_bookings_with_requests = [{
        'booking': booking,
        'request': booking.request
    } for booking in approved_bookings]

    print('filtered_bookings_with_requests:', filtered_bookings_with_requests)

    context = {
        'user': user,
        'managed_venues': managed_venues,
        'approved_bookings': filtered_bookings_with_requests
    }

    return render(request, 'venue_admin/approved_bookings.html', context)





def approved_cumulative_bookings_view(request):
    print('in approved_cumulative_bookings_view()')
    user = request.user

    if not user.is_authenticated:
        print('user is not authenticated')
        return render(request, 'venue_admin/cumulative_approved_bookings.html', {
            'user': None,
            'managed_venues': [],
            'approved_bookings': []
        })

    user_role = user.role.strip().lower()
    if user_role == 'venue_admin':
        managed_venues = Venue.objects.all()
    else:
        managed_venues = Venue.objects.filter(venue_admin=user.email)

    if not managed_venues.exists():
        return render(request, 'venue_admin/approved_bookings.html', {
            'user': user,
            'managed_venues': [],
            'approved_bookings': []
        })

    # ✅ Fetch only cumulative approved bookings
    # Step 1: Filter only cumulative request bookings
    approved_bookings = Booking.objects.filter(
        venue__in=managed_venues,
        status='active',
        request__cumulative_request_id__isnull=False  # <-- only cumulative requests
    ).select_related('user', 'venue', 'request')

    

    # Step 2: Deduplicate based on cumulative_request_id
    seen_cumulative_ids = set()
    unique_bookings = []

    for booking in approved_bookings:
        cumulative_id = booking.request.cumulative_request_id
        if cumulative_id and cumulative_id not in seen_cumulative_ids:
            seen_cumulative_ids.add(cumulative_id)
            unique_bookings.append({
                'booking': booking,
                'request': booking.request
            })

    print('unique_cumulative_bookings:', unique_bookings)

    print("\n==== Final Values Sent to Template ====")
    for item in unique_bookings:

        

        req = item['request']

        # Clean the event_details field in-place
        req.event_details = clean_multiline(req.event_details)
        req.additional_info = clean_multiline(req.additional_info)


        print(f"User Name: {req.user.name}")
        print(f"Organization Name: {req.organization_name}")
        print(f"Cumualative Request ID: {req.cumulative_request_id}")
        print(f"Venue: {req.venue.venue_name}")
        print(f"Date: {req.date}")
        print(f"Time: {req.time}")
        print(f"Duration: {req.duration}")
        # print(f"Event Details (truncated): {req.event_details[:50] + '...' if len(req.event_details) > 50 else req.event_details}")
        # print(f"Event Details: {req.event_details.replace('\n', ' ').replace('\r', ' ')}")
        print(f"Event Details: {req.event_details}")

        print("----------------------------------------")


    context = {
        'user': user,
        'managed_venues': managed_venues,
        'approved_bookings': unique_bookings
    }

    return render(request, 'venue_admin/cumulative_approved_bookings.html', context)










from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import VenueSelectForm, VenueEditForm
from gymkhana.models import Venue,Building


def venue_edit_start(request):
    if request.method == 'POST':
        venue_id = request.POST.get('venue')
        if venue_id:
            return redirect('venue_admin:venue_edit_form', venue_id=venue_id)
        else:
            messages.error(request, "Please select a venue")
    
    venues = Venue.objects.all().order_by('venue_name')
    return render(request, 'venue_admin/venue_edit.html', {
        'venues': venues,
        'venue': None
    })

# def venue_edit_form(request, venue_id):
#     try:
#         venue = Venue.objects.get(id=venue_id)
#     except Venue.DoesNotExist:
#         messages.error(request, "Venue not found")
#         return redirect('venue_edit_start')
    
#     if request.method == 'POST':
#         # Get building name for venue name generation
#         building_id = request.POST.get('building')
#         building_name = ""
#         if building_id:
#             try:
#                 building = Building.objects.get(id=building_id)
#                 building_name = building.name
#             except Building.DoesNotExist:
#                 pass
        
#         # Generate new venue name according to the formula
#         class_number = request.POST.get('class_number', '').strip()
#         floor_number = request.POST.get('floor_number', '').strip()
#         new_venue_name = f"{class_number}({building_name})_{floor_number}"
        
#         # Create a dictionary of updated values
#         updated_data = {
#             'venue_name': new_venue_name,
#             'description': request.POST.get('description'),
#             'photo_url': request.POST.get('photo_url'),
#             'capacity': request.POST.get('capacity'),
#             'class_type': request.POST.get('class_type'),
#             'class_number': class_number,
#             'length': request.POST.get('length'),
#             'depth_or_height': request.POST.get('depth_or_height'),
#             'area_sqm': request.POST.get('area_sqm'),
#             'building_id': building_id,
#             'floor_number': floor_number,
#             'room_number': request.POST.get('room_number'),
#             'campus': request.POST.get('campus'),
#             'address': request.POST.get('address'),
#             'venue_location': request.POST.get('venue_location'),
#             'facilities': request.POST.get('facilities'),
#             'usage_type': request.POST.get('usage_type'),
#             'department_incharge_id': request.POST.get('department_incharge'),
#             'dept_incharge_phone': request.POST.get('dept_incharge_phone'),
#             'dept_incharge_email': request.POST.get('dept_incharge_email'),
#             'dept_assistant_name1': request.POST.get('dept_assistant_name1'),
#             'dept_assistant_name2': request.POST.get('dept_assistant_name2'),
#             'venue_admin': request.POST.get('venue_admin'),
#             'picture_urls': request.POST.get('picture_urls'),
#         }
        
#         # Update the venue object
#         for field, value in updated_data.items():
#             if value is not None:
#                 setattr(venue, field, value)
        
#         try:
#             venue.save()
#             messages.success(request, "Venue updated successfully!")
#             return redirect('venue_edit_form', venue_id=venue_id)
#         except Exception as e:
#             messages.error(request, f"Error updating venue: {str(e)}")
    
#     # Prepare context for rendering
#     buildings = Building.objects.all()
#     users = CustomUser.objects.filter(is_active=True)
    
#     return render(request, 'venue_admin/venue_edit.html', {
#         'venue': venue,
#         'buildings': buildings,
#         'users': users,
#         'form': {  # Simulate form object for template
#             'description': {'value': venue.description},
#             'photo_url': {'value': venue.photo_url},
#             'capacity': {'value': venue.capacity},
#             'class_type': {'value': venue.class_type},
#             'class_number': {'value': venue.class_number},
#             'length': {'value': venue.length},
#             'depth_or_height': {'value': venue.depth_or_height},
#             'area_sqm': {'value': venue.area_sqm},
#             'building': {'value': venue.building_id},
#             'floor_number': {'value': venue.floor_number},
#             'room_number': {'value': venue.room_number},
#             'campus': {'value': venue.campus},
#             'address': {'value': venue.address},
#             'venue_location': {'value': venue.venue_location},
#             'facilities': {'value': venue.facilities},
#             'usage_type': {'value': venue.usage_type},
#             'department_incharge': {'value': venue.department_incharge_id},
#             'dept_incharge_phone': {'value': venue.dept_incharge_phone},
#             'dept_incharge_email': {'value': venue.dept_incharge_email},
#             'dept_assistant_name1': {'value': venue.dept_assistant_name1},
#             'dept_assistant_name2': {'value': venue.dept_assistant_name2},
#             'venue_admin': {'value': venue.venue_admin},
#             'picture_urls': {'value': venue.picture_urls},
#         }
#     })



def venue_edit_form(request, venue_id):
    try:
        venue = Venue.objects.get(id=venue_id)
    except Venue.DoesNotExist:
        messages.error(request, "Venue not found")
        return redirect('venue_edit_start')

    if request.method == 'POST':
        # Get building name for venue name generation
        building_id = request.POST.get('building')
        building_name = ""
        if building_id:
            try:
                building = Building.objects.get(id=building_id)
                building_name = building.name
            except Building.DoesNotExist:
                pass

        def get_post_value(field_name, strip=False):
            if field_name in request.POST:
                value = request.POST.get(field_name)
                return value.strip() if strip and value else value
            return None

        # Only generate a new venue name if all required parts exist
        class_number = get_post_value('class_number', strip=True)
        floor_number = get_post_value('floor_number', strip=True)
        if 'class_number' in request.POST and 'floor_number' in request.POST and 'building' in request.POST:
            new_venue_name = f"{class_number}({building_name})_{floor_number}"
            venue.venue_name = new_venue_name

        # List of fields we want to update if present
        fields_to_update = [
            'description', 'photo_url', 'capacity', 'class_type', 'class_number',
            'length', 'depth_or_height', 'area_sqm', 'building', 'floor_number',
            'room_number', 'campus', 'address', 'venue_location', 'facilities',
            'usage_type', 'department_incharge', 'dept_incharge_phone',
            'dept_incharge_email', 'dept_assistant_name1', 'dept_assistant_name2',
            'venue_admin', 'picture_urls'
        ]

        # Update only the fields that exist in request.POST
        for field in fields_to_update:
            if field in request.POST:
                value = request.POST.get(field)
                if field == 'building':
                    setattr(venue, 'building_id', value)
                elif field == 'department_incharge':
                    setattr(venue, 'department_incharge_id', value)
                else:
                    setattr(venue, field, value)

        try:
            venue.save()
            messages.success(request, "Venue updated successfully!")
            return redirect('venue_admin:venue_edit_form', venue_id=venue_id)
        except Exception as e:
            messages.error(request, f"Error updating venue: {str(e)}")

    # Prepare context for rendering
    buildings = Building.objects.all()
    users = CustomUser.objects.filter(is_active=True)

    return render(request, 'venue_admin/venue_edit.html', {
        'venue': venue,
        'buildings': buildings,
        'users': users,
        'form': {
            'description': {'value': venue.description},
            'photo_url': {'value': venue.photo_url},
            'capacity': {'value': venue.capacity},
            'class_type': {'value': venue.class_type},
            'class_number': {'value': venue.class_number},
            'length': {'value': venue.length},
            'depth_or_height': {'value': venue.depth_or_height},
            'area_sqm': {'value': venue.area_sqm},
            'building': {'value': venue.building_id},
            'floor_number': {'value': venue.floor_number},
            'room_number': {'value': venue.room_number},
            'campus': {'value': venue.campus},
            'address': {'value': venue.address},
            'venue_location': {'value': venue.venue_location},
            'facilities': {'value': venue.facilities},
            'usage_type': {'value': venue.usage_type},
            'department_incharge': {'value': venue.department_incharge_id},
            'dept_incharge_phone': {'value': venue.dept_incharge_phone},
            'dept_incharge_email': {'value': venue.dept_incharge_email},
            'dept_assistant_name1': {'value': venue.dept_assistant_name1},
            'dept_assistant_name2': {'value': venue.dept_assistant_name2},
            'venue_admin': {'value': venue.venue_admin},
            'picture_urls': {'value': venue.picture_urls},
        }
    })








from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.hashers import make_password

def user_list(request):
    users = CustomUser.objects.all().order_by('-created_at')
    return render(request, 'venue_admin/user_list.html', {'users': users})

def user_detail(request, user_id):
    user = get_object_or_404(CustomUser, id=user_id)
    return render(request, 'venue_admin/user_detail.html', {'user': user})

def add_user(request):
    if request.method == 'POST':
        try:
            # Create new user
            user = CustomUser(
                name=request.POST.get('name'),
                email=request.POST.get('email'),
                organization_name=request.POST.get('organization_name'),
                organization_type=request.POST.get('organization_type'),
                role=request.POST.get('role'),
                password=make_password(request.POST.get('password'))
            )
            user.save()
            messages.success(request, 'User added successfully!')
            return redirect('venue_admin:user_list')
        except Exception as e:
            messages.error(request, f'Error adding user: {str(e)}')
    return render(request, 'venue_admin/add_user.html')


from django.core.mail import send_mail
from django.conf import settings

def send_user_deletion_notification(user_name, user_email,deleter_action_name,deleter_action_email):
    """
    Sends an email to the sender's own email ID notifying that a user was deleted.
    """
    subject = "User Deletion Notification"
    message = f"The user '{user_name}' with email '{user_email}' has been deleted from the system by the user {deleter_action_email}"

    send_mail(
        subject=subject,
        message=message,
        from_email=sender_email,
        recipient_list=[sender_email],
        fail_silently=False,
    )




def delete_user(request, user_id):
    if request.method == 'POST':
        user = get_object_or_404(CustomUser, id=user_id)

        user_email = user.email
        user_name = user.name
        user.delete()

        # Try sending notification email
        try:
            deleter_action_name = request.session.get('name', 'Unknown User')
            deleter_action_email = request.session.get('email', 'no-reply@example.com')
            send_user_deletion_notification(user_name, user_email,deleter_action_name,deleter_action_email)
        except Exception as e:
            print(f"Failed to send deletion email: {e}")  # Optional: log this
            messages.warning(request, 'User deleted, but failed to send notification email.')

        messages.success(request, 'User deleted successfully!')
    return redirect('venue_admin:user_list')






from django.shortcuts import render, redirect
from django.contrib import messages
import uuid

def venue_create(request):
    buildings = Building.objects.all()
    
    if request.method == 'POST':
        print('inside venue_create()')
        # Manually extract all form data
        building_id = request.POST.get('building')
        floor_number = request.POST.get('floor_number')
        room_number = request.POST.get('room_number')
        class_number = request.POST.get('class_number')
        class_type = request.POST.get('class_type')
        
        try:
            # Create venue instance directly
            venue = Venue(
                id=uuid.uuid4(),
                building_id=building_id,
                floor_number=floor_number,
                room_number=room_number,
                class_number=class_number,
                class_type=class_type,
                capacity=request.POST.get('capacity'),
                description=request.POST.get('description'),
                photo_url=request.POST.get('photo_url'),
                address=request.POST.get('address'),
                # length=request.POST.get('length'),
                # depth_or_height=request.POST.get('depth_or_height'),
                # area_sqm=request.POST.get('area_sqm'),
                picture_urls=request.POST.get('picture_urls'),
                usage_type=request.POST.get('usage_type'),
                venue_location=request.POST.get('venue_location'),
                dept_incharge_phone=request.POST.get('dept_incharge_phone'),
                dept_incharge_email=request.POST.get('dept_incharge_email'),
                dept_assistant_name1=request.POST.get('dept_assistant_name1'),
                dept_assistant_name2=request.POST.get('dept_assistant_name2'),
                campus=request.POST.get('campus'),
                venue_admin=request.POST.get('venue_admin'),
                department_incharge_id=request.POST.get('department_incharge'),
                # Generate venue name
                venue_name=f"{class_number or room_number}({Building.objects.get(id=building_id).name})_{floor_number}"
            )
            
            # Save to database
            venue.save()
            
            messages.success(request, 'Venue created successfully!')
            return redirect('venue_admin:venue_edit_start')
            
        except Exception as e:
            messages.error(request, f'Error creating venue: {str(e)}')
            # Return form with previously entered values
            context = {
                'buildings': buildings,
                'form_data': request.POST,
                'error': str(e)
            }
            return render(request, 'venue_admin/venue_create.html', context)
    
    # GET request - show empty form
    context = {
        'buildings': buildings
    }
    return render(request, 'venue_admin/venue_create.html', context)



def send_venue_deleted_email(venue, deleted_by_user, deleted_by_user_email):
    print('\n\n--------start : send_venue_deleted_email-----------')

    admin_email = venue.venue_admin
    if not admin_email:
        print("Admin email not available.")
        return

    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = admin_email
    msg['Subject'] = "Venue Deleted Notification ❌"

    body = f"""
Dear Venue Admin,

This is to inform you that the following venue has been deleted from the system:

Venue Details:
- Name: {venue.venue_name}

Deleted By:
- Name: {deleted_by_user}
- Email: {deleted_by_user_email}

If this action was not authorized, please contact the system administrator immediately.

Regards,  
COEP Venue Booking System
"""

    msg.attach(MIMEText(body, 'plain'))

    try:
        context = ssl.create_default_context()
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls(context=context)
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, admin_email, msg.as_string())
            print(f"Venue deletion email sent to {admin_email}")
    except Exception as e:
        print(f"Failed to send venue deletion email: {e}")

    print('-----end send_venue_deleted_email--------')





def venue_delete(request, pk):
    venue = get_object_or_404(Venue, pk=pk)
    if request.method == 'POST':
        try:
            user_name = request.session.get('name', 'Unknown User')
            user_email = request.session.get('email', 'no-reply@example.com')
            send_venue_deleted_email(venue, user_name, user_email)
        except Exception as e:
            print(f"Error sending venue deletion email: {e}")
            
        venue.delete()
        messages.success(request, f'Venue {venue.venue_name} has been deleted successfully.')
        return redirect('venue_admin:venue_edit_start')
    return redirect('venue_admin:venue_edit', venue_id=pk)  







import traceback
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction
from django.shortcuts import get_object_or_404


@csrf_exempt  # Only if you're calling via JS without CSRF token; remove if not needed
def cumulative_cancel_booking(request, cumulative_request_id):
    if request.method == "POST":
        try:
            print('inside POST cumulative_cancel_booking()\n\n')

            print('cumulative_request_id->',cumulative_request_id)

            data = json.loads(request.body)
            reason = data.get('reason', '').strip()

            if not reason:
                return JsonResponse({
                    'success': False,
                    'message': 'Cancellation reason is required.'
                }, status=400)

            cumulative_req = get_object_or_404(CumulativeRequest, cumulative_request_id=cumulative_request_id)

            if cumulative_req.status != 'approved':
                return JsonResponse({
                    'success': False,
                    'message': 'Only approved cumulative bookings can be cancelled.'
                }, status=400)

            individual_requests = Request.objects.filter(
                cumulative_request_id=cumulative_request_id,
                status='approved'
            )

            print('individual_requests->',individual_requests)

            if not individual_requests.exists():
                return JsonResponse({
                    'success': False,
                    'message': 'No approved individual requests found to cancel.'
                }, status=404)

            with transaction.atomic():
                # Cancel each individual request
                for req in individual_requests:
                    req.status = 'user-cancelled'
                    req.reasons = reason
                    req.save(update_fields=["status", "reasons"])

                    # Cancel associated booking
                    try:
                        booking = req.booking
                        booking.status = 'user-cancelled'
                        booking.save(update_fields=["status"])
                    except Booking.DoesNotExist:
                        pass  # Safe to ignore if no booking was created

                # Cancel cumulative request
                cumulative_req.status = 'user-cancelled'
                cumulative_req.reasons = reason
                cumulative_req.accept = 0
                cumulative_req.reason_to_reject = reason
                cumulative_req.additional_comments = "Cancelled after approval"
                cumulative_req.save()

                print("\n\n\n\n")

                # print("individual_requests count:", individual_requests.count())
                # first_request = individual_requests.first()
                # print("First request:", first_request)

                print("individual_requests count:", len(individual_requests))
                first_request = individual_requests[0] if individual_requests else None
                print("First request:", first_request)


                print("\n\n\n\n")

                # Send email (same function used in rejection — adjust wording inside it if needed)
                send_cumulative_booking_rejected_email(
                    first_request, cumulative_req, None
                )

            return JsonResponse({
                'success': True,
                'message': 'Cumulative booking cancelled successfully.'
            })

        except json.JSONDecodeError:
            return JsonResponse({
                'success': False,
                'message': 'Invalid request data.'
            }, status=400)
        except Exception as e:
            print("Exception occurred in cumulative_cancel_booking:")
            traceback.print_exc()  # This prints the full traceback to the console or logs

            return JsonResponse({
                'success': False,
                'message': f'An unexpected error occurred: {str(e)}'
            }, status=500)

    return JsonResponse({
        'success': False,
        'message': 'Only POST method is allowed.'
    }, status=405)











from django.http import JsonResponse
from django.views import View
from django.core.serializers import serialize
from django.utils import timezone
from datetime import datetime, timedelta
import json





# class VenueListView(View):
    # def get(self, request):
    #     venues = Venue.objects.all().order_by('venue_name')
    #     print('inside GET VenueListView')
    #     print('venues->',venues)
    #     return render(request, 'users/venue_schedule.html', {'venues': venues})

from django.forms.models import model_to_dict



class VenueListView(View):
    def get(self, request):
        # venues = Venue.objects.all()

        # Order venues by venue_name
        venues = Venue.objects.all().order_by('venue_name')
        
        print('venues->', venues)
        
        # Manually create the dictionary instead of using model_to_dict
        venue_data = [{
            'id': str(venue.id),  # Convert UUID to string
            'venue_name': venue.venue_name
        } for venue in venues]
        
        print('venue_data->', venue_data)
        return render(request, 'venue_admin/venue_schedule.html', {'venue_data': venue_data})


class BookingScheduleAPI(View):

    def get(self, request):
        print('venue_admin : inside BookingScheduleAPI GET')
        print('venue_admin : inside BookingScheduleAPI GET')
        print('venue_admin : inside BookingScheduleAPI GET')
        print('venue_admin : inside BookingScheduleAPI GET')
        print('venue_admin : inside BookingScheduleAPI GET')

        venue_id = request.GET.get('venue_id')
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')

        print('venue_id->',venue_id)
        print('type(venue_id)->',type(venue_id))
        print('start_date->',start_date)
        print('end_date->',end_date)
        
        if not venue_id or not start_date or not end_date:
            return JsonResponse({'error': 'Missing required parameters'}, status=400)
        
        try:
            # Parse dates
            start_date_obj = datetime.strptime(start_date, '%Y-%m-%d').date()
            end_date_obj = datetime.strptime(end_date, '%Y-%m-%d').date()

            print('start_date_obj->',start_date_obj)
            print('end_date_obj->',end_date_obj)
            
            # Validate date range (max 30 days)
            if (end_date_obj - start_date_obj).days > 30:
                return JsonResponse({'error': 'Date range cannot exceed 30 days'}, status=400)

            print('after if condition')

            try:
                if not venue_id:  # Check if empty
                    print('in try block ---> not venue_id')
                    return JsonResponse({'error': 'venue_id cannot be empty'}, status=400)
                    
                print('venue_id before conversion->', venue_id, type(venue_id))
                # venue_uuid = uuid.UUID(str(venue_id).strip())  # Ensure it's string and remove whitespace
                venue_id_cleaned = str(venue_id).strip().replace('-', '')
                print('venue_id_cleaned->',venue_id_cleaned)
                venue_uuid = uuid.UUID(venue_id_cleaned)
                # venue_uuid = uuid.UUID(hex=venue_id_cleaned)

                print('venue_uuid->', venue_uuid)
            except ValueError as e:
                print(f'Conversion error: {str(e)}')
                return JsonResponse({'error': 'Invalid venue_id format - must be a valid UUID'}, status=400)
            

            
            # Get bookings for the venue and date range
            bookings = Booking.objects.filter(
                venue_id=venue_uuid,
                date__gte=start_date_obj,
                date__lte=end_date_obj,
                status='active'  # <-- Assuming 'active' is the approved status
            ).select_related('user', 'venue')

            print('bookings->',bookings)

            # For display (only approved)
            bookings = all_bookings.filter(status='active')
            
            # Prepare response data
            bookings_data = []
            for booking in bookings:
                bookings_data.append({
                    'id': str(booking.booking_id),
                    'date': booking.date.isoformat(),
                    'time': decimal_to_time_str(booking.time),  # Using the conversion function
                    'duration': booking.duration,
                    'event_details': booking.event_details,
                    'user_name': f"{booking.user.name}",
                    'status': booking.get_status_display(),
                    'venue_name': booking.venue.venue_name,
                    'email': booking.user.email,
                })
            print('bookings_data->',bookings_data)


            # Booking statistics
            status_counts = bookings.values('status').annotate(count=Count('venue_id'))
            print("\n\n\n")
            print('status_counts->',status_counts)
            print("\n\n\n")
            stats = {
                'total_bookings': bookings.count(),
                'active': 0,
                'cancelled': 0,
                'user_cancelled': 0,
            }

            for entry in status_counts:
                status = entry['status']
                count = entry['count']
                if status == 'active':
                    stats['active'] = count
                elif status == 'cancelled':
                    stats['cancelled'] = count
                elif status == 'user-cancelled':
                    stats['user_cancelled'] = count


            
            return JsonResponse({
                'bookings': bookings_data,
                'venue_id': venue_id,
                'start_date': start_date,
                'end_date': end_date,
                'booking_statistics': stats,
            })
            
        except ValueError as e:
            return JsonResponse({'error': 'Invalid date format'}, status=400)
        except Exception as e:
            print(f"Unexpected error: {str(e)}")
            print(f"Type: {type(e)}")
            import traceback
            traceback.print_exc()
            return JsonResponse({'error': str(e)}, status=500)


