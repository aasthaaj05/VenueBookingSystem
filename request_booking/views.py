

from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponse, HttpResponseNotAllowed
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q, F
from datetime import datetime, timedelta
import json
import sys
import traceback

from services import booking_service
from gymkhana.models import Booking
from .models import Venue, Request

import uuid


def format_time(value):
    """
    Convert time values like 10, 10.5, 13.5 into formatted string HH:MM.
    Handles None, null, or invalid values gracefully.
    """
    if value is None:
        return "Not specified"

    try:
        # Convert string to float if needed
        time_float = float(value)

        hours = int(time_float)
        minutes = 30 if (time_float - hours) == 0.5 else 0

        return f"{hours:02d}:{minutes:02d}"
    except (ValueError, TypeError):
        return str(value) or "Invalid time"





# Get list of venues
def get_venues(request):
    limit = int(request.GET.get('limit', 10))  # Default limit = 10
    try:
        venues = booking_service.getVenues(limit)
        return JsonResponse(venues, safe=False)
    except ValueError as e:
        return JsonResponse({'error': str(e)}, status=400)


# Get details of a specific venue
def get_venue_details(request, venue_id):
    print('hihih')
    try:
        print('asdswddd')
        venue = booking_service.getVenueDetails(venue_id)
        return JsonResponse(venue, safe=False)
    except ValueError as e:
        return JsonResponse({'error': str(e)}, status=400)


import json

def print_request_details(request):
    print("\n----- REQUEST DETAILS -----\n")

    # Print request method and path
    print(f"Method: {request.method}")
    print(f"Path: {request.path}")
    print(f"Content-Type: {request.content_type}")

    # Print headers
    print("\nHeaders:")
    for header, value in request.headers.items():
        print(f"{header}: {value}")

    # Print GET parameters
    if request.GET:
        print("\nGET Parameters:")
        for key, value in request.GET.items():
            print(f"{key}: {value}")

    # Print POST parameters
    if request.POST:
        print("\nPOST Parameters:")
        for key, value in request.POST.items():
            print(f"{key}: {value}")

    # Print raw request body
    try:
        body = request.body.decode('utf-8')
        print("\nRaw Body:", body)
        if request.content_type == "application/json":
            print("\nParsed JSON Body:", json.loads(body))  # Pretty print JSON body
    except json.JSONDecodeError:
        print("\nBody is not valid JSON")

    print("\n----- END REQUEST DETAILS -----\n")


from django.db.models import Count
from request_booking.models import Request, CumulativeRequest  # adjust if needed

from users.models import CustomUser

def cumulative_booking_status(request):
    # Get logged-in user
    user = request.user
    
    try:
        # Fetch user from CustomUser model
        user_obj = CustomUser.objects.get(email=user.email)
    except CustomUser.DoesNotExist:
        return render(request, 'request_booking/cumulative_booking_status.html', {
            'pending_requests': []
        })

    # Fetch all cumulative requests made by this user (regardless of status)
    cumulative_requests = CumulativeRequest.objects.select_related('venue', 'user').filter(
        user=user_obj
    ).order_by('-created_at')

    # Prepare the context data with all dates
    pending_cumulative_requests = []
    for cr in cumulative_requests:
        # Get all individual requests associated with this cumulative request
        individual_requests = Request.objects.filter(
            cumulative_request_id=cr.cumulative_request_id
        ).select_related('venue', 'user')
        
        # Format dates for display
        # dates = [req.date.strftime('%Y-%m-%d') for req in individual_requests]
        dates = sorted([req.date.strftime('%Y-%m-%d') for req in individual_requests])


        # unique_weekdays_list = list(dict.fromkeys(cr.weekdays))  # Preserves order
        # weekdays_string = ','.join(map(str, unique_weekdays_list))

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
        # print('clean_weekdays :', clean_weekdays)
        # print('weekday_names :', weekday_names)
        # print('weekday_str :', weekday_str)



        # print("----- Debug Info for CR (Cumulative Request) -----")
        # print("Accept:", cr.accept)
        # print("Reason to Approve:", cr.reason_to_approve)
        # print("Reason to Reject:", cr.reason_to_reject)
        # print("Additional Comments:", cr.additional_comments)
        # print("Suggest Alternate Venues:", cr.suggest_alternate_venues)
        # print("--------------------------------------------------------")

        
        pending_cumulative_requests.append({
            'cumulative_request_id': str(cr.cumulative_request_id),
            'email': cr.email or cr.user.email,
            'phone_number': cr.phone_number or cr.user.phone_number,
            'event_type': cr.event_type,
            'dates': dates,  # All dates from individual requests
            'start_date': cr.start_date.strftime('%Y-%m-%d'),
            'end_date': cr.end_date.strftime('%Y-%m-%d') if hasattr(cr, 'end_date') else None,
            'weekdays': weekday_str,  # String representation of weekdays
            'time': f"{cr.time}:00",
            'duration': f"{cr.duration}",
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
            'reasons': cr.reasons if cr.reasons else None,
            'purpose': cr.purpose if cr.purpose else 'N/A',
            'additional_info': individual_requests.first().additional_info if individual_requests.exists() else 'N/A',
            'special_requirements': cr.special_requirements,
            'individual_request_count': individual_requests.count(),
            'individual_requests': [str(req.request_id) for req in individual_requests],
            'accept':cr.accept,
            'reason_to_approve':cr.reason_to_approve,
            'reason_to_reject':cr.reason_to_reject,
            'additional_comments':cr.additional_comments,
            'suggest_alternate_venues':cr.suggest_alternate_venues
        })
        # print('pending_cumulative_requests : ', pending_cumulative_requests)

    context = {
        'pending_requests': pending_cumulative_requests,
        'person_name': user_obj.name,  # Add person_name to context
        'weekdays': ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"],
    }

    return render(request, 'request_booking/cumulative_booking_status.html', context)


def time_str_to_decimal(time_str):
    hour, minute = map(int, time_str.split(":"))
    return hour + (minute / 60)


# @csrf_exempt  # Disable CSRF protection for testing (remove in production)
def get_available_slots(request):
    if request.method == "POST":
        try:
            print()
            print()
            print('in get_available_lots')
            print_request_details(request)
            print('Request received:', request)

            # Parse JSON data from request body
            data = json.loads(request.body.decode("utf-8"))  # Correct way to parse JSON

            print("Received Data:", data)

            # Extract start_date from request data
            start_date = data.get("date")
            end_date = data.get("end_date", start_date)  # Default end_date to start_date if missing

            print('in get_available_slots function')
            print('start_date : ' , start_date)

            print(f"Start Date: {start_date}, End Date: {end_date}")

            start_time_str = data.get("start_time")  # e.g., "6:00 PM"
            end_time_str = data.get("end_time")      # e.g., "7:00 PM"

            

            # Convert 12-hour format to 24-hour format
            # start_hour = int(datetime.strptime(start_time_str, "%I:%M %p").strftime("%H"))
            # end_hour = int(datetime.strptime(end_time_str, "%I:%M %p").strftime("%H"))
            start_hour = time_str_to_decimal(start_time_str)
            end_hour = time_str_to_decimal(end_time_str)

            print()
            print()

            print("Start Hour:", start_hour)  # Output: "18"
            print("End Hour:", end_hour)      # Output: "19"

            print("type of Start Hour:", type(start_hour))  # Output: "18"
            print("type of End Hour:", type(end_hour))      # Output: "19"

            print("Start Hour:", start_hour)  # Output: "18"

            # Print the results
            print("Start time:", start_hour)
            print("End time:", end_hour)

            print()
            print()
            print()



            print('start time : ' , start_hour)
            print('end time : ' , end_hour)

            request.session['start_date'] = start_date
            request.session['end_date'] = end_date
            request.session['start_time'] = start_hour
            request.session['end_time'] = end_hour


            # Convert string times to datetime objects
            time_format = "%I:%M %p"  # Format for "6:00 PM"
            # start_time = datetime.strptime(start_time_str, time_format)
            # end_time = datetime.strptime(end_time_str, time_format)
            start_time=start_hour
            end_time=end_hour

            print()
            print()
            print('in ')

            # Calculate duration in hours
            # duration = int((end_time - start_time).total_seconds() // 3600)  # Convert seconds to hours

            # duration = int((int(end_hour) - int(start_hour))) 
            duration = end_hour - start_hour
            request.session["booking_duration"] = duration

            print('in get_available_slots func duration : ' , duration)

            # Store duration in session
            request.session["booking_duration"] = duration

            print('-----')
            print('duration : ' , duration)

            print()
            print()
            print('in get_available_slots fuc ')
            print('start_date : ' , start_date)
            print('end date : ' , end_date)
            print('start time : ' , start_time)
            print('end time : ' , end_time)
            print()
            print()

            if not start_date:
                return JsonResponse({'error': 'Missing start_date'}, status=400)

            # Get all venues
            venues = Venue.objects.all().values('id', 'venue_name')  # Get all venue IDs & names
            all_slots = {}

            print('Processing venues...')

            for venue in venues:
                print('Checking availability for venue:', venue['venue_name'])
                venue_id = venue['id']
                venue_name = venue['venue_name']

                # Create a new mutable request dictionary for each venue
                request_data = data.copy()
                request_data["venue_id"] = venue_id

                # Call the existing function get_available_slots_1()
                response = get_available_slots_1(request_data)

                if isinstance(response, JsonResponse) and response.status_code == 200:
                    all_slots[venue_name] = json.loads(response.content)  # Convert JSONResponse to dict
                else:
                    all_slots[venue_name] = {'error': 'Could not fetch slots'}

   
            print('all slots : ')
            print(all_slots)

                # Store in session to access in the next view
            request.session['all_slots'] = all_slots
          
      

            return JsonResponse({
                "message": "Booking successful",
                "redirect_url": "/request_booking/book_venue"
            })


        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON format"}, status=400)

        return JsonResponse({"error": "Invalid request method"}, status=405)






import json
from django.http import JsonResponse
from django.core.exceptions import ObjectDoesNotExist



import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from django.conf import settings  # Import settings

sender_email = settings.EMAIL_HOST_USER
sender_password = settings.EMAIL_HOST_PASSWORD
smtp_server = settings.EMAIL_HOST
smtp_port = settings.EMAIL_PORT


def getUnavailableSlots(request):
    if request.method == "GET":
        return JsonResponse({"error": "Invalid request method"}, status=405)

    try:
        venue_name = request.session.get('venue_name')
        print("VENUE_NAME:", venue_name)
        data = json.loads(request.body)
        date = data.get('date')
        resp = booking_service.getUnavailableSlots(venue_name, date)
        print("unavailable slots: ", resp)
        return JsonResponse({'unavailable_slots': resp}, safe=False)
    except ObjectDoesNotExist as e:
        return JsonResponse({'error': "Requested object does not exist"}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)  # Convert exception to string

# def get_buildings(request):
#     buildings = Venue.objects.values_list('building_name', flat=True).distinct()
#     return render(request, 'request_booking/building.html', {'buildings': buildings})

from django.shortcuts import render
from gymkhana.models import Building  # Import Building model

def get_buildings(request):
    buildings = Building.objects.values_list('name', flat=True).distinct()  # Fetch building names
    return render(request, 'request_booking/building.html', {'buildings': buildings})




from django.http import HttpResponseNotAllowed
from django.shortcuts import render
from gymkhana.models import Venue

from django.http import HttpResponseNotAllowed
from django.shortcuts import render
from gymkhana.models import Venue
from django.db.models.functions import Lower
from django.db.models.functions import Lower

def user_dashboard(request, building_name=None):  # Accept building_name
    if request.method == "GET":
        print("Inside user_dashboard view")
        print("Building Name:", building_name)  # Debugging output

        # Fetch all venues from the database and sort alphabetically by venue_name
        venues = Venue.objects.all().order_by(Lower('venue_name'))  

        if building_name:
            venues = venues.filter(building__name=building_name)  # ✅ Correct field reference

        venues = venues.values('id', 'venue_name', 'capacity', 'facilities', 'photo_url')

        # Map the venue data with availability
        formatted_venues = []

        for venue in venues:
            venue_name = venue['venue_name']
            formatted_venues.append({
                "id": venue['id'],
                "name": venue_name,
                "capacity": venue['capacity'],
                "facilities": venue['facilities'],
                "images": venue['photo_url'].split(",") if venue['photo_url'] else [],
            })

        return render(request, 'request_booking/user_dashboard.html', {
            "venues": formatted_venues,
            "building_name": building_name  # Pass building name to template
        })

    return HttpResponseNotAllowed(['GET'])





def get_available_slots_1(request_data):
    print(request_data)
    venue_id = request_data.get('venue_id')  # Access dictionary keys directly
    start_date = request_data.get('date')
    print(venue_id)
    print(start_date)


    end_date = start_date  # or request_data.get('end_date', start_date)

    if not venue_id or not start_date or not end_date:
        return JsonResponse({'error': 'Missing parameters'}, status=400)

    try:
        slots = booking_service.getAvailableSlots(venue_id, start_date, end_date)
        return JsonResponse(slots, safe=False)
    except ValueError as e:
        return JsonResponse({'error': str(e)}, status=400)

    





# Request a slot (POST)
# @csrf_exempt  # Disable CSRF for testing; remove this in production
def request_slot(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Only POST method allowed'}, status=405)

    data = json.loads(request.body)
    required_fields = ['venue_id', 'user_id', 'date', 'time', 'duration', 'alternate_venues', 'event_details', 'need']

    if not all(field in data for field in required_fields):
        return JsonResponse({'error': 'Missing required fields'}, status=400)

    try:
        print(*data)
        result = booking_service.requestSlot(**data)
        return JsonResponse({'success': result})
    except ValueError as e:
        return JsonResponse({'error': str(e)}, status=400)

# Cancel a booking request (POST)
# @csrf_exempt
def cancel_request(request, request_id):
    # if request.method != 'POST':
    #     return JsonResponse({'error': 'Only POST method allowed'}, status=405)

    # data = json.loads(request.body)
    req_id = request_id
    req_id = req_id.replace('-', '')  # Remove all hyphens


    if not req_id:
        return JsonResponse({'error': 'Missing request ID'}, status=400)

    try:
        result = booking_service.cancelRequest(req_id)
        return redirect('/request_booking/booking_status')
    except ValueError as e:
        return JsonResponse({'error': str(e)}, status=400)

# Get user requests
def get_user_requests(request):
    user_id = request.GET.get('user_id')

    if not user_id:
        return JsonResponse({'error': 'Missing user ID'}, status=400)

    try:
        requests = booking_service.getUserRequests(user_id)
        return JsonResponse(requests, safe=False)
    except ValueError as e:
        return JsonResponse({'error': str(e)}, status=400)


def float_to_time_str(t):
    hours = int(t)
    minutes = int((t - hours) * 60)
    return f"{hours:02d}:{minutes:02d}"
    



# @csrf_exempt
def book_venue(request):
    print()
    print()
    print("in book_venue func...")
    print()
    print()
    """Handles venue selection and preloads user session details."""
    

    if request.method == "POST":
        print('in book_venue function')
        venue_name = request.POST.get("venue_name")
        # print(f"Venue selected: {venue_name}")

        # Print session data for debugging
        print("Session Data:", request.session.items())
        print(request.session.get("name"))
        venues = Venue.objects.all().exclude(name = venue_name)  # Fetch all venues from the database

        # Fetch user details from session
        user_data = {
            "name": request.session.get("name"),  # Full name from session
            "email": request.session.get("email"),
            "organization_name": request.session.get("organization_name"),
            "date": request.session.get("start_date"),  # Extracting start date
            "start_time": request.session.get("start_time"),  # Extracting start time
            "end_time": request.session.get("end_time"),  # Extracting end time
        }

        print('user data : ' , user_data)

        return render(request, "request_booking/booking_form.html", {
            "venue": venue_name,
            "user_data": user_data,
            'venues':venues,# Passing session data to prefill the form
        })

    if request.method == "GET":
        print("in GET GET book_venue func...")
        # Print session data for debugging
        print("Session Data:", request.session.items())
        print(request.session.get("name"))
        venues = Venue.objects.all()

        venue_name = request.session.get("venue_name")

        print("Venue name stored in session:", venue_name)  # Debugging print


        # Fetch user details from session
        # Fetch user details from session
        user_data = {
            "name": request.session.get("name"),  # Full name from session
            "email": request.session.get("email"),
            "organization_name": request.session.get("organization_name"),
            "date": request.session.get("start_date"),  # Extracting start date
            # "start_time": f"{request.session.get('start_time'):02d}:00",  # Convert to HH:MM format
            # "end_time": f"{request.session.get('end_time'):02d}:00",  # Convert to HH:MM format
            "start_time": float_to_time_str(request.session.get("start_time")),
            "end_time": float_to_time_str(request.session.get("end_time")),
    }

        print('user data : ' , user_data)
        
        return render(request, "request_booking/booking_form.html", {
            "venue": venue_name,
            "user_data": user_data,
            'venues':venues,  # Passing session data to prefill the form
        })






from datetime import datetime
from django.utils.timezone import now  # Handles timezone-aware datetime



from datetime import datetime
import json
from django.http import JsonResponse
from django.shortcuts import redirect
from django.views.decorators.csrf import csrf_exempt
from django.utils.timezone import now  # Handles timezone-aware datetime
from .models import Request, Venue





from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from datetime import datetime
from .models import Request, Venue

from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from datetime import datetime
from .models import Request, Venue

def time_str_to_float(time_str):
    """Convert 'HH:MM' string to float hours, e.g. '14:30' -> 14.5"""
    if ":" in time_str:
        hour, minute = map(int, time_str.split(":"))
        return hour + (minute / 60) 
    else:
        return float(time_str)
        


@login_required
def process_booking(request):
    print()
    print()
    print('in process_booking() ')
    print()
    print()
    print()
    if request.method == "POST":
        user = request.user  # Get the logged-in user
        print(f"User: {user}")


        venue_id = Venue.objects.get(venue_name = request.session.get("venue_name") ) 

        event_type = request.POST.get("eventType")
        full_name = request.POST.get("fullName")
        email = request.POST.get("email", user.email)
        organization_name = request.POST.get("organization_name")
        date = request.POST.get("start_date")
        start_time = request.POST.get("start_time")
        end_time = request.POST.get("end_time")
        phone_number = request.POST.get("phone")
        guest_count = request.POST.get("guestCount")
        alt_venue_1_id = request.POST.get("alternateVenue1")
        alt_venue_2_id = request.POST.get("alternateVenue2", None)
        event_details = request.POST.get("eventDetails")
        purpose = request.POST.get("purpose", "")
        special_requirements = request.POST.get("specialRequirements", "")

        print(f"Received Form Data: Venue={venue_id}, Event Type={event_type}, Full Name={full_name}, Email={email}, Org={organization_name}")
        print(f"Date={date}, Start Time={start_time}, End Time={end_time}, Phone={phone_number}, Guest Count={guest_count}")
        print(f"Alt Venue 1={alt_venue_1_id}, Alt Venue 2={alt_venue_2_id}, Event Details={event_details}, Purpose={purpose}")

        print('special_requirements : ', special_requirements)
        print('special_requirements : ', special_requirements)
        print('special_requirements : ', special_requirements)

        # Convert date and time to appropriate formats
        try:
            # start_time_obj = datetime.strptime(start_time, "%H:%M").time()
            # end_time_obj = datetime.strptime(end_time, "%H:%M").time()
            # Convert string time to datetime.time object
            # start_time_obj = datetime.strptime(start_time, "%H:%M").time()
            # end_time_obj = datetime.strptime(end_time, "%H:%M").time()

            # Extract only the hour as an integer
            # start_time = start_time_obj.hour
            # end_time = end_time_obj.hour
            # start_time = float(start_time)
            # end_time = float(end_time_obj)

            start_time = time_str_to_float(start_time)
            end_time = time_str_to_float(end_time)

            print('start , end time : ',start_time, end_time)  # Example Output: 11, 22
            date_obj = datetime.strptime(date, "%Y-%m-%d").date()

            # Compute the difference
            duration = end_time - start_time

            # Calculate duration in minutes
            # duration = (datetime.combine(date_obj, end_time_obj) - datetime.combine(date_obj, start_time_obj)).seconds // 60
            # print(f"Parsed Date: {date_obj}, Start Time: {start_time_obj}, End Time: {end_time_obj}, Duration: {duration} minutes")

            # Fetch venue instances
            venue = Venue.objects.get(venue_name=venue_id)
            alternate_venue_1 = Venue.objects.get(id=alt_venue_1_id)
            alternate_venue_2 = Venue.objects.get(id=alt_venue_2_id) if alt_venue_2_id else None

            print(f"Selected Venue: {venue.venue_name}")
            print(f"Alternate Venue 1: {alternate_venue_1.venue_name}")
            if alternate_venue_2:
                print(f"Alternate Venue 2: {alternate_venue_2.venue_name}")


            # Check if a similar request already exists
            existing_request = Request.objects.filter(
                user=user,
                email=email,
                date=date_obj,
                time=start_time,
                venue=venue,
            ).exists()

            if existing_request:
                send_duplicate_request_email(user, email, venue, date_obj, start_time)
                return redirect("request_booking:index")  # Redirect to home or bookings list 

            # Get the current time
            current_time = datetime.now()

             # Format the current time in a human-readable format
            formatted_time = current_time.strftime("%Y-%m-%d %H:%M:%S")

            print("Current Time:", formatted_time)


            send_booking_request_email(request, venue, alternate_venue_1, alternate_venue_2,event_type, purpose , formatted_time)
            # to_email, requester_name, booking_id, venue, date, time_slot, purpose
            send_forwarded_notification(email , request, venue, alternate_venue_1, alternate_venue_2,event_type, purpose , formatted_time)


            # Create request object
            booking_request = Request.objects.create(
                user=user,
                email=email,
                phone_number=phone_number,
                event_type=event_type,
                additional_info=purpose,
                date=date_obj,
                time=start_time,
                duration=duration,
                venue=venue,
                status='pending',
                need=organization_name,  # Using need to store organization name
                organization_name = organization_name,
                alternate_venue_1=alternate_venue_1,
                alternate_venue_2=alternate_venue_2,
                event_details=event_details,
                guest_count = guest_count,
                special_requirements=special_requirements,
               
            )


            

            print(f"Booking Request Created: {booking_request}")
            messages.success(request, "Booking request submitted successfully!")
            return redirect("faculty_advisor:home")  # Redirect to home or bookings list

        except Venue.DoesNotExist:
            print("Error: Invalid venue ID provided.")
            messages.error(request, "Invalid venue selection. Please try again.")
        except ValueError as ve:
            print(f"Error: Invalid date/time format. Exception: {ve}")
            messages.error(request, "Invalid date/time format. Please check and try again.")

    return redirect("request_booking:booking_status")

def check_venue_availability_mul_weeks(venue, start_date, end_date, weekdays, time, duration):
    print('in check_venue_availability_mul_weeks()')
    # Ensure start_date is a date object, not datetime
    if isinstance(start_date, datetime):
        start_date = start_date.date()
    if isinstance(end_date, datetime):
        end_date = end_date.date()

    current_date = start_date
    while current_date <= end_date:
        existing_bookings = Booking.objects.filter(
            venue=venue,
            date=current_date,
            status='active'
        )

        for booking in existing_bookings:
            booking_start = float(booking.time)
            booking_end = float(booking.time) + float(booking.duration)
            request_start = float(time)
            request_end = float(time) + float(duration)

            if request_start < booking_end and request_end > booking_start:
                print("❌ Conflict detected with booking:", booking)
                print(f"Date: {current_date}, Requested: {request_start}-{request_end}, Booking: {booking_start}-{booking_end}")
                return False

        current_date += timedelta(days=1)

    return True



'''
def cumulative_send_confirmation_email_to_requester(email, full_name, venue_obj, event_type, purpose, start_date, end_date, start_time, booking_duration, weekdays):
    print('---------in cumulative_send_confirmation_email_to_requester()------')

    if not email:
        print("Requester email not found.")
        return

    weekday_names = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
    readable_weekdays = ", ".join(weekday_names[int(d)] for d in weekdays)

    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = email
    msg['Subject'] = "Your Venue Booking Request Has Been Initiated"

    body = f"""
Dear {full_name},

Your venue booking request has been successfully initiated.

Request Details:
- Venue: {venue_obj.venue_name}
- Date Range: {start_date} to {end_date}
- Days: {readable_weekdays}
- Time: {format_time_float_to_string(start_time)}
- Duration: {format_duration_float_to_string(booking_duration)}
- Purpose: {purpose}
- Event Type: {event_type}
- Status: Initiated

We will notify you once your request is reviewed by the venue admin.

Regards,
COEP Venue Booking System
"""

    msg.attach(MIMEText(body, 'plain'))

    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.send_message(msg)
        print(f"Confirmation email sent to requester: {email}")
    except Exception as e:
        print(f"Failed to send email to {email}: {e}")

    print('---------Ended ---- cumulative_send_confirmation_email_to_requester()------')






def cumulative_send_booking_request_email_to_admin(
    email, full_name, venue_obj, event_type, purpose, start_date, end_date, start_time, booking_duration, weekdays
):
    print('---------in cumulative_send_booking_request_email_to_admin()------')

    if not email:
        print("Admin email not found.")
        return

    weekday_names = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
    readable_weekdays = ", ".join(weekday_names[int(d)] for d in weekdays)

    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = email
    msg['Subject'] = "New Venue Booking Request Initiated"

    body = f"""
Dear Admin,
A new cumulative venue booking request has been initiated.
Request Details:
- Venue: {venue_obj.venue_name}
- Date Range: {start_date} to {end_date}
- Days: {readable_weekdays}
- Time: {format_time_float_to_string(start_time)}
- Duration: {format_duration_float_to_string(booking_duration)}
- Purpose: {purpose}
- Event Type: {event_type}
- Status: Pending

Please review the request and take the necessary action.

Regards,
COEP Venue Booking System
"""

    msg.attach(MIMEText(body, 'plain'))

    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.send_message(msg)
        print(f"Booking request email sent to venue admin: {email}")
    except Exception as e:
        print(f"Failed to send booking request email: {e}")

    print('---------Ended ---- cumulative_send_booking_request_email_to_admin()------')


'''


def cumulative_send_confirmation_email_to_requester(
    email, full_name, venue_obj, event_type, purpose, start_date, end_date, start_time, booking_duration, weekdays, total_days
):
    print('---------in cumulative_send_confirmation_email_to_requester()------')

    if not email:
        print("Requester email not found.")
        return

    # Convert weekday names to readable format
    weekday_names = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
    
    # Handle weekdays - they might be strings like "Tuesday" or integers
    readable_weekdays_list = []
    for day in weekdays:
        if isinstance(day, str) and day.isdigit():
            # If it's a string number like "0", "1", etc.
            day_idx = int(day)
            if 0 <= day_idx < len(weekday_names):
                readable_weekdays_list.append(weekday_names[day_idx])
        elif isinstance(day, int):
            # If it's already an integer
            if 0 <= day < len(weekday_names):
                readable_weekdays_list.append(weekday_names[day])
        else:
            # If it's already a weekday name like "Tuesday"
            readable_weekdays_list.append(day)
    
    readable_weekdays = ", ".join(readable_weekdays_list)

    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = email
    msg['Subject'] = "Your Cumulative Venue Booking Request Submitted Successfully"

    body = f"""
Dear {full_name},
Your cumulative venue booking request has been submitted successfully.

Request Details:
- Venue: {venue_obj.venue_name}
- Date Range: {start_date} to {end_date}
- Total Days: {total_days} days
- Days: {readable_weekdays}
- Time: {format_time_float_to_string(start_time)}
- Duration: {format_duration_float_to_string(booking_duration)}
- Purpose: {purpose}
- Event Type: {event_type}
- Status: Pending

Your request is now pending approval from the venue admin. 
You will receive an email once your request has been reviewed.

Regards,
COEP Venue Booking System
"""

    msg.attach(MIMEText(body, 'plain'))

    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.send_message(msg)
        print(f"Confirmation email sent to requester: {email}")
    except Exception as e:
        print(f"Failed to send confirmation email: {e}")

    print('---------Ended ---- cumulative_send_confirmation_email_to_requester()------')






def cumulative_send_booking_request_email_to_admin(
    email, full_name, venue_obj, event_type, purpose, start_date, end_date, start_time, booking_duration, weekdays, total_days
):
    print('---------in cumulative_send_booking_request_email_to_admin()------')

    if not email:
        print("Admin email not found.")
        return

    # Convert weekday names to readable format
    weekday_names = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
    
    # Handle weekdays - they might be strings like "Tuesday" or integers
    readable_weekdays_list = []
    for day in weekdays:
        if isinstance(day, str) and day.isdigit():
            # If it's a string number like "0", "1", etc.
            day_idx = int(day)
            if 0 <= day_idx < len(weekday_names):
                readable_weekdays_list.append(weekday_names[day_idx])
        elif isinstance(day, int):
            # If it's already an integer
            if 0 <= day < len(weekday_names):
                readable_weekdays_list.append(weekday_names[day])
        else:
            # If it's already a weekday name like "Tuesday"
            readable_weekdays_list.append(day)
    
    readable_weekdays = ", ".join(readable_weekdays_list)

    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = email
    msg['Subject'] = "New Venue Booking Request Initiated"

    body = f"""
Dear Admin,
A new cumulative venue booking request has been initiated.

Requester Details:
- Name: {full_name}
- Venue: {venue_obj.venue_name}

Request Details:
- Date Range: {start_date} to {end_date}
- Total Days: {total_days} days
- Days: {readable_weekdays}
- Time: {format_time_float_to_string(start_time)}
- Duration: {format_duration_float_to_string(booking_duration)}
- Purpose: {purpose}
- Event Type: {event_type}
- Status: Pending

Please review the request and take the necessary action.

Regards,
COEP Venue Booking System
"""

    msg.attach(MIMEText(body, 'plain'))

    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.send_message(msg)
        print(f"Booking request email sent to venue admin: {email}")
    except Exception as e:
        print(f"Failed to send booking request email: {e}")

    print('---------Ended ---- cumulative_send_booking_request_email_to_admin()------')











# original code
'''
@login_required
def process_booking_multiple(request):
    print('---process_booking_multiple---\n\n\n')
    if request.method == "POST":
       
        print('---POST yyy process_booking_multiple---\n\n\n')
     
        # Print all keys in POST data and request.body
        print("POST keys:", request.POST.keys())
        print("POST data type:", type(request.POST))
        print("Request body type:", type(request.body))
        
        user = request.user
        print(f"User: {user}")

        try:
            # Get form data
            venue_id = request.POST.get("venue")
            venue = Venue.objects.get(id=venue_id)

            event_type = request.POST.get("eventType")
            full_name = request.POST.get("full_name")
            email = request.POST.get("email", user.email)
            organization_name = request.POST.get("organization_name")
            start_date_str = request.POST.get("start_date_str")
            start_time_str = request.POST.get("start_time_str")
            end_time_str = request.POST.get("end_time_str")
            phone_number = request.POST.get("phone_number")
            guest_count = request.POST.get("guest_count")
            event_details = request.POST.get("event_details")
            purpose = request.POST.get("purpose", "")
            special_requirements = request.POST.get("special_requirements", "")
            ss = request.POST.get("special_requirements", "")
            end_date_str = request.POST.get("end_date")  # Get end_date from POST

            print(ss)
            print(ss)
            print('[[[[[[[[[]]]]]]]]]')
            
            
            # #num_weeks = int(request.POST.get("num_weeks", 1))
            # start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()

            # num_weeks_str = request.POST.get("num_weeks")

            # if not num_weeks_str:
            #     messages.error(request, "Number of weeks is required.")
            #     return redirect("request_booking:booking_status")

            # num_weeks = int(num_weeks_str)

            # end_date = start_date + timedelta(weeks=num_weeks) - timedelta(days=1)



            start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()

            if not end_date_str:
                messages.error(request, "End date is required.")
                return redirect("request_booking:booking_status")
                
            end_date = datetime.strptime(end_date_str, "%Y-%m-%d").date()

            # Validate that end_date is not before start_date
            if end_date < start_date:
                messages.error(request, "End date cannot be before start date.")
                return redirect("request_booking:booking_status")




            weekdays = request.POST.getlist("weekdays")  # Should be list of strings like ["0", "2", "4"]

            print('enue.dept_incharge_email : ', venue.dept_incharge_email)

            # Print form data and types
            print("Form Data and Types:")
            print(f"venue_id: {venue_id} (type: {type(venue_id).__name__})")
            print(f"venue: {venue} (type: {type(venue).__name__})")
            print(f"event_type: {event_type} (type: {type(event_type).__name__})")
            print(f"full_name: {full_name} (type: {type(full_name).__name__})")
            print(f"email: {email} (type: {type(email).__name__})")
            print(f"organization_name: {organization_name} (type: {type(organization_name).__name__})")
            print(f"start_date_str: {start_date_str} (type: {type(start_date_str).__name__})")
            print(f"start_time_str: {start_time_str} (type: {type(start_time_str).__name__})")
            print(f"end_time_str: {end_time_str} (type: {type(end_time_str).__name__})")
            print(f"phone_number: {phone_number} (type: {type(phone_number).__name__})")
            print(f"guest_count: {guest_count} (type: {type(guest_count).__name__})")
            print(f"event_details: {event_details} (type: {type(event_details).__name__})")
            print(f"purpose: {purpose} (type: {type(purpose).__name__})")
            print(f"special_requirements: {special_requirements} (type: {type(special_requirements).__name__})")
            print(f"weekdays: {weekdays} (type: {type(weekdays).__name__})")
            print(f"end_date: {end_date} (type: {type(end_date).__name__})")
            print(f"Duration in days: {(end_date - start_date).days + 1} days")

            print()
            print()
            print()

            print(f"weekdays (raw): {weekdays}")
            weekdays = sorted([int(day) for day in weekdays])
            print(f"Parsed weekdays: {weekdays}")

            print('lkvjdspojvojofjoifuoiujeoajwoihjo')
            print('lkvjdspojvojofjoifuoiujeoajwoihjo')
            print('lkvjdspojvojofjoifuoiujeoajwoihjo')
            print('lkvjdspojvojofjoifuoiujeoajwoihjo')

            # Time parsing
            
            start_time = time_str_to_float(start_time_str)
            print('start_time',start_time)
            end_time = time_str_to_float(end_time_str)
            print('end_time',end_time)
            duration = end_time - start_time
            print('duration',duration)
            start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()
            print('start_date',start_date)
            # start_date = int(start_date_str)
            # end_date = datetime.strptime(end_date_str, "%Y-%m-%d").date()

            created_count = 0

           

            # Generate a unique cumulative request ID
            cumulative_request_id = uuid.uuid4()

            event_type = request.session.get('eventType')
            print('event_type : ', event_type)

            cumulative_req = CumulativeRequest.objects.create(
                cumulative_request_id=cumulative_request_id,
                user=user,
                full_name=full_name,
                email=email,
                phone_number=phone_number,
                organization_name=organization_name,
                event_type=event_type,
                guest_count=guest_count,
                event_details=event_details,
                purpose=purpose,
                special_requirements=special_requirements,
                venue=venue,
                start_date=start_date,
                end_date=end_date,               
                #num_weeks=num_weeks,
                weekdays=",".join([str(day) for day in weekdays]),  # Store as comma-separated string
                time=start_time,
                duration=duration,
                status='waiting_for_approval'
            )
            # Create a mapping from day names to numbers (Monday=0)
            DAY_TO_NUM = {
                'Monday': 0,
                'Tuesday': 1,
                'Wednesday': 2,
                'Thursday': 3,
                'Friday': 4,
                'Saturday': 5,
                'Sunday': 6
            }

            weekdays = list(dict.fromkeys(weekdays))  # Removes duplicates while preserving order
            



            current_date = start_date

            while current_date <= end_date:
                if current_date.weekday() in weekdays:
                    mail_start_time = start_time
                    mail_duration = duration

                    new_req = Request.objects.create(
                        user=user,
                        email=email,
                        phone_number=phone_number,
                        full_name=full_name,
                        organization_name=organization_name,
                        event_type=event_type,
                        guest_count=guest_count,
                        additional_info=purpose,
                        date=current_date,
                        time=start_time,
                        duration=duration,
                        venue=venue,
                        need=organization_name,
                        alternate_venue_1=None,
                        alternate_venue_2=None,
                        event_details=event_details,
                        special_requirements=special_requirements,
                        status='pending',
                        cumulative_booking=True,
                        cumulative_request_id=cumulative_request_id
                    )

                    print(f"Created request for {current_date}")
                    created_count += 1

                current_date += timedelta(days=1)


            print('iuikkkkkkkddjq87701740970')
            print('iuikkkkkkkddjq87701740970')
            print('iuikkkkkkkddjq87701740970')
            # Reverse the dictionary: from {0: 'Monday', 1: 'Tuesday', ...}
            NUM_TO_DAY = {v: k for k, v in DAY_TO_NUM.items()}
            weekday_names = tuple([NUM_TO_DAY[num] for num in weekdays])

            print("Parsed weekday names:", weekday_names)

            try:
                cumulative_send_confirmation_email_to_requester(
                    email=email,
                    full_name=full_name,
                    venue_obj=venue,
                    event_type=event_type,
                    purpose=purpose,
                    start_date=start_date,
                    start_time=mail_start_time,
                    booking_duration=mail_duration,  # Update this if your logic has actual duration
                    #num_week = num_weeks,
                    weekdays = weekday_names,
                )
            except Exception as e:
                print(f"Failed to send confirmation email to requester: {e}")

            try:
                cumulative_send_booking_request_email_to_admin(email=venue.venue_admin,
                    full_name=full_name,
                    venue_obj=venue,
                    event_type=event_type,
                    purpose=purpose,
                    start_date=start_date,
                    start_time=mail_start_time,
                    booking_duration=mail_duration,  # Update this if your logic has actual duration
                    #num_week = num_weeks,
                    weekdays = weekday_names)

            except Exception as e:
                print(f"Failed to send confirmation email to requester: {e}")

            print('iuikkkkkkkddjq87701740970')
            print()
            print()

            if created_count:
                messages.success(request, f"{created_count} booking request(s) submitted successfully!")
            else:
                messages.warning(request, "No requests were created (conflicts or duplicates).")

            return redirect("faculty_advisor:home")

        except Venue.DoesNotExist:
            print("Invalid venue.")
            messages.error(request, "Invalid venue selected.")
        except ValueError as ve:
            print(f"ValueError: {ve}")
            messages.error(request, "Invalid input. Please check your form.")

        return redirect("request_booking:booking_status")
    else:
        venues = Venue.objects.all()
        print("heherer ewrewrhewjwhrjwh in request multiple")
        return render(request, "request_booking/check_multiple_week_avail.html", {"venues": venues})
'''



@login_required
def process_booking_multiple(request):
    print('---process_booking_multiple---\n\n\n')
    if request.method == "POST":
        print('---POST yyy process_booking_multiple---\n\n\n')
        
        user = request.user
        print(f"User: {user}")

        try:
            # Get form data
            venue_id = request.POST.get("venue")
            venue = Venue.objects.get(id=venue_id)

            event_type = request.POST.get("eventType")
            full_name = request.POST.get("full_name")
            email = request.POST.get("email", user.email)
            organization_name = request.POST.get("organization_name")
            start_date_str = request.POST.get("start_date_str")
            end_date_str = request.POST.get("end_date")
            start_time_str = request.POST.get("start_time_str")
            end_time_str = request.POST.get("end_time_str")
            phone_number = request.POST.get("phone_number")
            guest_count = request.POST.get("guest_count")
            event_details = request.POST.get("event_details")
            purpose = request.POST.get("purpose", "")
            special_requirements = request.POST.get("special_requirements", "")
            
            # Parse dates
            start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()
            
            if not end_date_str:
                messages.error(request, "End date is required.")
                return redirect("request_booking:booking_status")
                
            end_date = datetime.strptime(end_date_str, "%Y-%m-%d").date()
            
            # Validate that end_date is not before start_date
            if end_date < start_date:
                messages.error(request, "End date cannot be before start date.")
                return redirect("request_booking:booking_status")

            weekdays = request.POST.getlist("weekdays")
            weekdays = sorted([int(day) for day in weekdays])
            
            # ✅ Find all matching dates in the range
            matching_dates = []
            check_date = start_date
            while check_date <= end_date:
                if check_date.weekday() in weekdays:
                    matching_dates.append(check_date)
                check_date += timedelta(days=1)
            
            # ✅ Validate that there are matching dates
            if not matching_dates:
                DAY_TO_NUM = {
                    'Monday': 0, 'Tuesday': 1, 'Wednesday': 2, 'Thursday': 3,
                    'Friday': 4, 'Saturday': 5, 'Sunday': 6
                }
                NUM_TO_DAY = {v: k for k, v in DAY_TO_NUM.items()}
                selected_days = ', '.join([NUM_TO_DAY[day] for day in weekdays])
                messages.error(
                    request, 
                    f"No {selected_days} found between {start_date.strftime('%b %d, %Y')} and {end_date.strftime('%b %d, %Y')}. "
                    f"Please select a date range that includes these days."
                )
                return redirect("request_booking:booking_status")

            print(f"Matching dates found: {len(matching_dates)}")
            print(f"Dates: {[d.strftime('%Y-%m-%d (%A)') for d in matching_dates]}")

            # Time parsing
            start_time = time_str_to_float(start_time_str)
            end_time = time_str_to_float(end_time_str)
            duration = end_time - start_time

            # Create a mapping from day names to numbers
            DAY_TO_NUM = {
                'Monday': 0, 'Tuesday': 1, 'Wednesday': 2, 'Thursday': 3,
                'Friday': 4, 'Saturday': 5, 'Sunday': 6
            }
            NUM_TO_DAY = {v: k for k, v in DAY_TO_NUM.items()}
            weekday_names = tuple([NUM_TO_DAY[num] for num in weekdays])

            # Generate a unique cumulative request ID
            cumulative_request_id = uuid.uuid4()

            if not event_type:
                event_type = request.session.get('eventType')

            cumulative_req = CumulativeRequest.objects.create(
                cumulative_request_id=cumulative_request_id,
                user=user,
                full_name=full_name,
                email=email,
                phone_number=phone_number,
                organization_name=organization_name,
                event_type=event_type,
                guest_count=guest_count,
                event_details=event_details,
                purpose=purpose,
                special_requirements=special_requirements,
                venue=venue,
                start_date=start_date,
                end_date=end_date,
                weekdays=",".join([str(day) for day in weekdays]),
                time=start_time,
                duration=duration,
                status='waiting_for_approval'
            )

            weekdays = list(dict.fromkeys(weekdays))  # Remove duplicates
            created_count = 0

            # ✅ Create requests for each matching date
            for current_date in matching_dates:
                new_req = Request.objects.create(
                    user=user,
                    email=email,
                    phone_number=phone_number,
                    full_name=full_name,
                    organization_name=organization_name,
                    event_type=event_type,
                    guest_count=guest_count,
                    additional_info=purpose,
                    date=current_date,
                    time=start_time,
                    duration=duration,
                    venue=venue,
                    need=organization_name,
                    alternate_venue_1=None,
                    alternate_venue_2=None,
                    event_details=event_details,
                    special_requirements=special_requirements,
                    status='pending',
                    cumulative_booking=True,
                    cumulative_request_id=cumulative_request_id
                )

                print(f"✅ Created request for {current_date.strftime('%Y-%m-%d (%A)')}")
                created_count += 1

            # Send emails
            try:
                cumulative_send_confirmation_email_to_requester(
                    email=email,
                    full_name=full_name,
                    venue_obj=venue,
                    event_type=event_type,
                    purpose=purpose,
                    start_date=start_date,
                    end_date=end_date,
                    start_time=start_time,
                    booking_duration=duration,
                    weekdays=weekday_names,
                    total_days=created_count
                )
            except Exception as e:
                print(f"Failed to send confirmation email to requester: {e}")

            try:
                cumulative_send_booking_request_email_to_admin(
                    email=venue.venue_admin,
                    full_name=full_name,
                    venue_obj=venue,
                    event_type=event_type,
                    purpose=purpose,
                    start_date=start_date,
                    end_date=end_date,
                    start_time=start_time,
                    booking_duration=duration,
                    weekdays=weekday_names,
                    total_days=created_count
                )
            except Exception as e:
                print(f"Failed to send confirmation email to admin: {e}")

            if created_count:
                messages.success(request, f"{created_count} booking request(s) submitted successfully!")
            else:
                messages.warning(request, "No requests were created.")

            return redirect("faculty_advisor:home")

        except Venue.DoesNotExist:
            print("Invalid venue.")
            messages.error(request, "Invalid venue selected.")
        except ValueError as ve:
            print(f"ValueError: {ve}")
            messages.error(request, "Invalid input. Please check your form.")
        except Exception as e:
            print(f"Error: {e}")
            import traceback
            traceback.print_exc()
            messages.error(request, "An error occurred while processing your request.")

        return redirect("request_booking:booking_status")
    else:
        venues = Venue.objects.all()
        return render(request, "request_booking/check_multiple_week_avail.html", {"venues": venues})






from datetime import datetime, timedelta
from django.utils.timezone import make_aware
from django.db.models import Q
import calendar




from datetime import datetime, timedelta
from django.http import JsonResponse
from django.shortcuts import render

def check_multiple_week_availability_view(request):
    if request.method == 'POST':
        try:
            start_date_str = request.POST.get("start_date")
            end_date_str = request.POST.get("end_date")
            weekdays = request.POST.getlist("weekdays")

            # Convert inputs
            start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()
            end_date = datetime.strptime(end_date_str, "%Y-%m-%d").date()
            weekdays = [int(day) for day in weekdays]

            if end_date < start_date:
                return JsonResponse({
                    "status": "error",
                    "message": "End date cannot be before start date"
                }, status=400)

            # ✅ First, find all matching dates in the range
            matching_dates = []
            check_date = start_date
            while check_date <= end_date:
                if check_date.weekday() in weekdays:
                    matching_dates.append(check_date)
                check_date += timedelta(days=1)

            # ✅ Validate that there are matching dates
            if not matching_dates:
                weekday_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
                selected_days = ', '.join([weekday_names[day] for day in weekdays])
                return JsonResponse({
                    "status": "error",
                    "message": f"No {selected_days} found between {start_date.strftime('%b %d, %Y')} and {end_date.strftime('%b %d, %Y')}. Please select a date range that includes these days."
                }, status=400)

            venues = Venue.objects.all().order_by(Lower('venue_name'))
            available_venues = []

            user = request.user

            start_time_str = request.POST.get("start_time")
            end_time_str = request.POST.get("end_time")
            phone_number = request.POST.get("phone")
            guest_count = request.POST.get("guestCount")
            event_details = request.POST.get("eventDetails")
            purpose = request.POST.get("purpose", "")
            special_requirements = request.POST.get("specialRequirements", "")

            start_hour = float(start_time_str)
            end_hour = float(end_time_str)
            duration = float(end_hour - start_hour)

            # Debugging output
            print(f"Start Date: {start_date}")
            print(f"End Date: {end_date}")
            print(f"Matching dates found: {len(matching_dates)}")
            print(f"Matching dates: {[d.strftime('%Y-%m-%d (%A)') for d in matching_dates]}")
            print(f"Start Time: {start_time_str}")
            print(f"End Time: {end_time_str}")
            print(f"Weekdays: {weekdays}")

            for venue in venues:
                is_available = True

                # ✅ Check availability for each matching date
                for current_date in matching_dates:
                    existing_bookings = Booking.objects.filter(
                        venue=venue,
                        date=current_date,
                        status='active'
                    )

                    for booking in existing_bookings:
                        booking_start = float(booking.time)
                        booking_end = booking_start + float(booking.duration)
                        request_start = float(start_hour)
                        request_end = request_start + float(duration)

                        if request_start < booking_end and request_end > booking_start:
                            is_available = False
                            print(f"❌ Conflict at {venue.venue_name} on {current_date.strftime('%Y-%m-%d (%A)')}")
                            break

                    if not is_available:
                        break

                if is_available:
                    available_venues.append({
                        "id": venue.id,
                        "venue_name": venue.venue_name,
                        "capacity": venue.capacity,
                    })

            print(f"✅ Available venues: {len(available_venues)}")

            return JsonResponse({
                "status": "success",
                "venues": available_venues,
                "matching_dates_count": len(matching_dates),
                "matching_dates": [d.strftime('%Y-%m-%d') for d in matching_dates]
            })

        except Exception as e:
            import traceback
            traceback.print_exc()
            return JsonResponse({
                "status": "error",
                "message": f"Error occurred: {str(e)}"
            }, status=400)

    else:
        return render(request, "request_booking/check_multiple_week_avail.html")


import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart





# utils/email_utils.py

from django.core.mail import send_mail

def send_duplicate_request_email(user, email, venue, date_obj, start_time):
    subject = "Duplicate Booking Request Detected"
    message = f"""Dear {user.name},

Our records show that you have already made a similar venue booking request with the following details:

📌 Venue        : {venue}
📅 Date         : {date_obj}
⏰ Time Slot    : {start_time}
📨 Email        : {email}

If this was unintentional, you may ignore this message. Otherwise, your earlier request is already in process.

Regards,  
Venue Booking System  
CSI COEP Tech
"""

    send_mail(
        subject,
        message,
        sender_email,   # From email
        (email, ),                  # Recipient list
        fail_silently=False,
    )




def format_time_float_to_string(time_input):
    """Converts float or string time (e.g., 8.5 or '8.5') to 'HH:MM' format (e.g., '08:30')"""
    try:
        time_float = float(time_input)
        hours = int(time_float)
        minutes = int(round((time_float - hours) * 60))
        return f"{hours:02d}:{minutes:02d}"
    except (ValueError, TypeError):
        return "Invalid time"







def send_forwarded_notification(to_email , request, venue_obj, alt_venue_1, alt_venue_2, event_type,purpose , formatted_time):
    # Get venue in-charge email
    
    print()
    print('---------in send_forwarded_notification()------')
    print()
    print('to_email : ' , to_email)
    print()
    
    if not to_email:
        print("Venue in-charge email not found.")
        return

    # Retrieve booking details from session
    start_date = request.session.get('start_date')
    start_time = request.session.get('start_time')
    booking_duration = request.session.get('booking_duration')

    # Email content
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = to_email
    msg['Subject'] = "Venue Booking Request has been initiated"

    body = f"""
    Dear ,

    Your new venue booking request has been initiated.

    Request Details:
    - Requested by: {request.user.name} ({request.user.email})
    - Venue: {venue_obj.venue_name}
    - Date: {start_date}
    - Time: {format_time_float_to_string(start_time)}
    - Duration: {format_duration_float_to_string(booking_duration)}
    - Purpose: {purpose}
    - Event Type: {event_type}
    - Alternate Venue 1: {alt_venue_1.venue_name if alt_venue_1 else 'None'}
    - Alternate Venue 2: {alt_venue_2.venue_name if alt_venue_2 else 'None'}
    - Status: Pending


    Regards,  
    COEP Venue Booking System
    """

    msg.attach(MIMEText(body, 'plain'))

    # Send email
    with smtplib.SMTP(smtp_server, smtp_port) as server:
        server.starttls()
        server.login(sender_email, sender_password)
        server.send_message(msg)

    print(f"Venue booking request email sent to {to_email}")

    print('---------Ended ---- send_booking_request_email()------')







# Example usage:
# send_booking_request_email(request, venue_obj, alt_venue_1, alt_venue_2, data, "Pending")

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from django.utils.timezone import now

def format_duration_float_to_string(duration_float):
    """Converts float duration (e.g., 6.5) to 'X hours Y mins'"""
    hours = int(duration_float)
    minutes = int(round((duration_float - hours) * 60))
    if minutes == 0:
        return f"{hours} hours"
    else:
        return f"{hours} hours {minutes} mins"


def send_booking_request_email(request, venue_obj, alt_venue_1, alt_venue_2, event_type,purpose , formatted_time):
    # Get venue in-charge email
    # venue_incharge_email = venue_obj.department_incharge.email if venue_obj.department_incharge else None
    venue_incharge_email = venue_obj.venue_admin
    print()
    print('---------in send_booking_request_email()------')
    print()
    print('venue_incharge_email : ' , venue_incharge_email)
    print()
    
    if not venue_incharge_email:
        print("Venue in-charge email not found.")
        return

    # Retrieve booking details from session
    start_date = request.session.get('start_date')
    start_time = request.session.get('start_time')
    booking_duration = request.session.get('booking_duration')

   

 

    # Email content
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = venue_incharge_email
    msg['Subject'] = "New Venue Booking Request"

    body = f"""
    Dear Admin,

    A new venue booking request has been submitted.

    Request Details:
    - Requested by: {request.user.name} ({request.user.email})
    - Venue: {venue_obj.venue_name}
    - Date: {start_date}
    - Time: {format_time_float_to_string(start_time)}
    - Duration: {format_duration_float_to_string(booking_duration)}
    - Purpose: {purpose}
    - Event Type: {event_type}
    - Alternate Venue 1: {alt_venue_1.venue_name if alt_venue_1 else 'None'}
    - Alternate Venue 2: {alt_venue_2.venue_name if alt_venue_2 else 'None'}
    - Status: Pending

    Please review the request and take the necessary action.

    Regards,  
    COEP Venue Booking System
    """

    msg.attach(MIMEText(body, 'plain'))

    # Send email
    with smtplib.SMTP(smtp_server, smtp_port) as server:
        server.starttls()
        server.login(sender_email, sender_password)
        server.send_message(msg)

    print(f"Venue booking request email sent to {venue_incharge_email}")

    print('---------Ended ---- send_booking_request_email()------')

# Example usage:
# send_booking_request_email(request, venue_obj, alt_venue_1, alt_venue_2, data, "Pending")













def format_duration(duration_float):
    try:
        duration_float = float(duration_float)  # 👈 convert to float first
        hours = int(duration_float)
        minutes = int(round((duration_float - hours) * 60))
        return f"{hours:02d} hours {minutes:02d} mins"
    except (ValueError, TypeError):
        return "Invalid"












from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Request



@login_required
def booking_status(request):
    """
    View to fetch and display booking requests for the logged-in user only.
    """
    print()
    print()
    print('in booking_status() ')
    print()
    print()
    print()
    print()
    
    user_id = request.session.get('user_id')  # Get the logged-in user's ID from session

    if not user_id:
        return JsonResponse({"error": "User ID not found in session"}, status=400)

    # Fetch only the requests made by the logged-in user
    requests = Request.objects.filter(user_id=user_id, cumulative_booking='0').select_related('venue').order_by('-date')

    print(f"User ID: {user_id}, Requests: {requests}")  # Debugging

    person_name = request.session.get('name')

    print('\n\nin booking status function\n\n')
    

    for req in requests:
        req.formatted_duration = format_duration(req.duration)
    

    return render(request, "request_booking/booking_status.html", {"requests": requests , "person_name": person_name})


from django.shortcuts import render
from .models import Venue

def venue_list(request):
    # Fetch all venue details
    venues = Venue.objects.all()

    # Format venue data for the template
    venue_data = []
    for venue in venues:
        facilities_list = [facility.strip() for facility in venue.facilities.split(',')] if venue.facilities else [] 
        venue_data.append({
            "id": venue.id,
            "name": venue.venue_name,
            "capacity": venue.capacity,
            "facilities": facilities_list, 
            "images": venue.photo_url.split(',') if venue.photo_url else [],  # Assuming multiple images are comma-separated
        })

    print("VENUE DETAILS:", venue_data)

    context = {
        'venues': venue_data
    }

    return render(request, 'request_booking/user_dashboard.html', context)  # Replace 'your_template.html' with your actual template filename


def index(request):
    return render(request , 'request_booking/index.html')











def send_cancellation_email_to_user(user_email, user_name, venue_name, event_date, event_time, cancel_reason):
    if not user_email:
        print("User email not found. Skipping email.")
        return

    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = user_email
    msg['Subject'] = "Booking Cancellation Confirmation"

    body = f"""
    Dear {user_name},

    You have cancelled your booking for the following event.

    Cancellation Details:
    - Venue: {venue_name}
    - Date: {event_date}
    - Time: {format_time_float_to_string(event_time)}
    - Reason: {cancel_reason}

    If this cancellation was not intended or if you have any questions, please contact the admin team.

    Regards,  
    COEP Venue Booking System
    """

    msg.attach(MIMEText(body, 'plain'))

    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.send_message(msg)

        print(f"Cancellation email sent to {user_email}")
    except Exception as e:
        print(f"Failed to send cancellation email: {e}")





def send_cumulative_req_cancellation_email_to_user(cumulative_req,cancel_msg):
    user_email = cumulative_req.user.email
    if not cumulative_req.user.email:
        print("User email not found. Skipping email.")
        return

    print('inside send_cumulative_req_cancellation_email_to_user()')

    print('cumulative_req.time->',cumulative_req.time)
    print('type(cumulative_req.time)->',type(cumulative_req.time))
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = cumulative_req.user.email
    msg['Subject'] = "Booking Cancellation Confirmation"

    body = f"""
    Dear {cumulative_req.user.name},

    You have cancelled your booking for the following event.

    Cancellation Details:
    - Venue: {cumulative_req.venue.venue_name}
    - Date: {cumulative_req.start_date}
    - Duration: {cumulative_req.duration}
    - Time: {format_time_float_to_string(cumulative_req.time)}
    - Reason: {cancel_msg}

    If this cancellation was not intended or if you have any questions, please contact the admin team.

    Regards,  
    COEP Venue Booking System
    """

    msg.attach(MIMEText(body, 'plain'))

    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.send_message(msg)

        print(f"Cancellation email sent to {cumulative_req.user.email}")
    except Exception as e:
        print(f"Failed to send cancellation email: {e}")









def cancel_booking(request):
    print('\n\n---cancel_booking()---\n\n')
    print('\n\n---cancel_booking()---\n\n')
    print('\n\n---cancel_booking()---\n\n')
    print('\n\n---cancel_booking()---\n\n')
    
    if request.method == 'POST':
        request_id = request.POST.get('request_id')
        cancel_reason = request.POST.get('cancel_reason')

        print("cancel_reason:", cancel_reason)

        try:
            req_obj = Request.objects.get(request_id=request_id, user=request.user)

            # Handle cancellation based on status
            if req_obj.status == 'approved':
                print('approved')
                print('approved')
                print('approved')
                print('approved')
                print('approved')
                print('approved')
                # Booking exists → cancel both
                try:
                    booking = Booking.objects.get(request=req_obj, user=request.user)
                    
                    # Update booking status
                    booking.status = 'user-cancelled'
                    booking.msg = cancel_reason
                    booking.save()

                    # Update request status
                    req_obj.status = 'user-cancelled'
                    req_obj.reasons = cancel_reason
                    req_obj.save()

                    send_cancellation_email_to_user(
                        user_email=booking.user.email,
                        user_name=booking.user.name,
                        venue_name=booking.venue.venue_name,
                        event_date=booking.date,
                        event_time=booking.time,
                        cancel_reason=cancel_reason
                    )

                    messages.success(request, 'Approved booking has been cancelled successfully.')
                    return redirect('/request_booking/booking_status')

                except Booking.DoesNotExist:
                    messages.error(request, 'Approved booking not found.')
                    return redirect('/request_booking/booking_status')

            elif req_obj.status == 'pending':
                print('pending')
                print('pending')
                print('pending')
                print('pending')
                print('pending')
                print('pending')
                # Only Request exists → cancel request
                req_obj.status = 'user-cancelled'
                req_obj.reasons = cancel_reason
                req_obj.save()

                send_cancellation_email_to_user(
                    user_email=request.user.email,
                    user_name=request.user.name,
                    venue_name=req_obj.venue.venue_name,
                    event_date=req_obj.date,
                    event_time=req_obj.time,
                    cancel_reason=cancel_reason
                )

                messages.success(request, 'Pending request has been cancelled successfully.')
                return redirect('/request_booking/booking_status')

            else:
                messages.error(request, f'Cannot cancel a request with status: {req_obj.status}')
                return redirect('/request_booking/booking_status')

        except Request.DoesNotExist:
            messages.error(request, 'Request not found or you are not authorized to cancel it.')
            return redirect('/request_booking/booking_status')

    # If not POST, redirect back
    return redirect('/request_booking/booking_status')









def cumulative_cancel_booking(request):
    print('\n\n---cumulative_cancel_booking()---\n\n')
    
    if request.method == 'POST':
        received_id = request.POST.get('request_id')  # This could be either request_id or cumulative_request_id
        cancel_reason = request.POST.get('cancel_reason')

        print("cancel_reason:", cancel_reason)

        try:
            # First try to find a regular request with this ID
            try:
                req_obj = Request.objects.get(request_id=received_id, user=request.user)
                is_cumulative = False
            except Request.DoesNotExist:
                # If not found, try to find a cumulative request
                try:
                    print('try to find a cumulative request')
                    cumulative_request = CumulativeRequest.objects.get(
                        cumulative_request_id=received_id,
                        user=request.user
                    )
                    is_cumulative = True
                except CumulativeRequest.DoesNotExist:
                    messages.error(request, 'Request not found or you are not authorized to cancel it.')
                    return redirect('/request_booking/cumulative_booking_status')

            if is_cumulative:
                # Handle cumulative booking cancellation
                print('Handle cumulative booking cancellation')
                related_requests = Request.objects.filter(
                    cumulative_request_id=received_id,
                    user=request.user
                )
                
                # Cancel all related requests
                print('Cancel all related requests')
                for r in related_requests:
                    if r.status == 'approved':
                        try:
                            booking = Booking.objects.get(request=r, user=request.user)
                            booking.status = 'user-cancelled'
                            booking.msg = cancel_reason
                            booking.save()
                        except Booking.DoesNotExist:
                            pass
                    
                    r.status = 'user-cancelled'
                    r.reasons = cancel_reason
                    r.save()

                # Cancel the cumulative request
                cumulative_request.status = 'user-cancelled'
                cumulative_request.reason_to_reject = cancel_reason
                cumulative_request.save()
                print('Cancel the cumulative request')

                # # Send cancellation email
                # send_cancellation_email_to_user(
                #     user_email=request.user.email,
                #     user_name=request.user.name,
                #     venue_name=cumulative_request.venue.venue_name,
                #     event_date=cumulative_request.start_date,
                #     event_time=cumulative_request.time,
                #     cancel_reason=cancel_reason,
                #     is_cumulative=True
                # )

                messages.success(request, 'Your recurring booking has been cancelled successfully.')
                return redirect('/request_booking/cumulative_booking_status')

            else:
                # Handle single request cancellation
                if req_obj.status == 'approved':
                    try:
                        booking = Booking.objects.get(request=req_obj, user=request.user)
                        
                        booking.status = 'user-cancelled'
                        booking.msg = cancel_reason
                        booking.save()

                        req_obj.status = 'user-cancelled'
                        req_obj.reasons = cancel_reason
                        req_obj.save()

                        send_cancellation_email_to_user(
                            user_email=booking.user.email,
                            user_name=booking.user.name,
                            venue_name=booking.venue.venue_name,
                            event_date=booking.date,
                            event_time=booking.time,
                            cancel_reason=cancel_reason
                        )

                        messages.success(request, 'Your booking has been cancelled successfully.')
                        return redirect('/request_booking/cumulative_booking_status')

                    except Booking.DoesNotExist:
                        messages.error(request, 'Approved booking not found.')
                        return redirect('/request_booking/cumulative_booking_status')

                elif req_obj.status == 'pending':
                    req_obj.status = 'user-cancelled'
                    req_obj.reasons = cancel_reason
                    req_obj.save()
                    print('inside cumulative_cancel_booking : req_obj.save()')

                    # send_cancellation_email_to_user(
                    #     user_email=request.user.email,
                    #     user_name=request.user.name,
                    #     venue_name=req_obj.venue.venue_name,
                    #     event_date=req_obj.date,
                    #     event_time=req_obj.time,
                    #     cancel_reason=cancel_reason
                    # )

                    messages.success(request, 'Your pending request has been cancelled successfully.')
                    return redirect('/request_booking/cumulative_booking_status')

                else:
                    messages.error(request, f'Cannot cancel a request with status: {req_obj.status}')
                    return redirect('/request_booking/cumulative_booking_status')

        except Exception as e:
            print(f"Error cancelling booking: {str(e)}")
            messages.error(request, 'An error occurred while processing your cancellation.')
            return redirect('/request_booking/cumulative_booking_status')

    return redirect('/request_booking/cumulative_booking_status')

from datetime import datetime, timedelta
from django.db.models.functions import Lower

def arnav_check_multiple_week_availability_view(request):
    if request.method == 'POST':
        print('POST check_multiple_week_availability_view')

        start_date_str = request.POST.get("start_date")
        end_date_str = request.POST.get("end_date")
        weekdays = request.POST.getlist("weekdays")

        # Convert inputs
        start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()
        end_date = datetime.strptime(end_date_str, "%Y-%m-%d").date()
        weekdays = [int(day) for day in weekdays]

        if end_date < start_date:
            print("End date before start date")
            return []

        # ✅ First, find all matching dates in the range
        matching_dates = []
        check_date = start_date
        while check_date <= end_date:
            if check_date.weekday() in weekdays:
                matching_dates.append(check_date)
            check_date += timedelta(days=1)

        # ✅ If no matching dates, return empty list
        if not matching_dates:
            print(f"No matching weekdays found in date range")
            return []

        venues = Venue.objects.all().order_by(Lower('venue_name'))
        available_venues = []

        user = request.user
    
        start_time_str = request.POST.get("start_time")
        end_time_str = request.POST.get("end_time")
        phone_number = request.POST.get("phone")
        guest_count = request.POST.get("guestCount")
        event_details = request.POST.get("eventDetails")
        purpose = request.POST.get("purpose", "")
        special_requirements = request.POST.get("specialRequirements", "")

        start_hour = float(start_time_str)
        end_hour = float(end_time_str)
        duration = float(end_hour - start_hour)

        # Debugging output
        print(f"Start Date: {start_date}")
        print(f"End Date: {end_date}")
        print(f"Matching dates: {[d.strftime('%Y-%m-%d (%A)') for d in matching_dates]}")
        print(f"Start Time: {start_time_str}")
        print(f"End Time: {end_time_str}")
        print(f"Weekdays: {weekdays}")
        print(f"Duration: {duration}")

        for venue in venues:
            is_available = True

            # ✅ Check each matching date
            for current_date in matching_dates:
                existing_bookings = Booking.objects.filter(
                    venue=venue,
                    date=current_date,
                    status='active'
                )

                for booking in existing_bookings:
                    booking_start = float(booking.time)
                    booking_end = booking_start + float(booking.duration)
                    request_start = float(start_hour)
                    request_end = request_start + float(duration)

                    if request_start < booking_end and request_end > booking_start:
                        is_available = False
                        print(f"❌ Conflict at {venue.venue_name} on {current_date.strftime('%Y-%m-%d (%A)')}")
                        break

                if not is_available:
                    break

            if is_available:
                available_venues.append(venue)

        print(f"✅ venues available: {len(available_venues)}")

        return available_venues


    #     except Exception as e:
    #         return JsonResponse({
    #             "status": "error",
    #             "message": f"Error occurred: {str(e)}"
    #         }, status=400)

    # else:
    #     return render(request, "request_booking/check_multiple_week_avail.html")





from django.shortcuts import render
from django.views import View
from django.http import HttpResponse
import pprint

class RequestMultipleWeekAvailabilityView(View):
    def get(self, request, *args, **kwargs):
        venues = Venue.objects.all()
        
        # Fetch user details from session
        user_data = {
            "name": request.session.get("name"),
            "email": request.session.get("email"),
            "organization_name": request.session.get("organization_name"),
            "date": request.session.get("start_date"),
            "start_time": request.session.get("start_time"),
            "end_time": request.session.get("end_time"),
        }

        return render(request, "request_booking/check_multiple_week_avail.html", {
            "venue_list": venues, 
            "user_data": user_data
        })

    def post(self, request, *args, **kwargs):
        print('in RequestMultipleWeekAvailabilityView POST')

        # Store form data in session first
        request.session['venue'] = request.POST.get('venue')
        request.session['eventType'] = request.POST.get('eventType')
        request.session['fullName'] = request.POST.get('fullName')
        request.session['email'] = request.POST.get('email')
        request.session['organization_name'] = request.POST.get('organization_name')
        request.session['start_date'] = request.POST.get('start_date')
        request.session['end_date'] = request.POST.get('end_date')
        request.session['start_time'] = request.POST.get('start_time')
        request.session['end_time'] = request.POST.get('end_time')
        request.session['weekdays'] = request.POST.getlist('weekdays')
        request.session['phone'] = request.POST.get('phone')
        request.session['guestCount'] = request.POST.get('guestCount')
        request.session['eventDetails'] = request.POST.get('eventDetails')
        request.session['purpose'] = request.POST.get('purpose')
        request.session['specialRequirements'] = request.POST.get('specialRequirements')
        request.session['terms'] = request.POST.get('terms')
        request.session.modified = True

        # ✅ Calculate matching dates for display FIRST
        start_date_str = request.POST.get('start_date')
        end_date_str = request.POST.get('end_date')
        weekdays = [int(day) for day in request.POST.getlist('weekdays')]
        
        start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()
        end_date = datetime.strptime(end_date_str, "%Y-%m-%d").date()
        
        matching_dates = []
        check_date = start_date
        while check_date <= end_date:
            if check_date.weekday() in weekdays:
                matching_dates.append(check_date)
            check_date += timedelta(days=1)
        
        # Create weekday names string
        DAY_NAMES = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        selected_weekdays = ', '.join([DAY_NAMES[day] for day in sorted(weekdays)])
        
        if not matching_dates:
            print(f"❌ No matching dates found for weekdays {weekdays} in range {start_date} to {end_date}")
            return render(request, 'request_booking/select_multiple_venues.html', {
                "venues": [],
                'eventType': request.session.get('eventType'),
                'fullName': request.session.get('fullName'),
                'email': request.session.get('email'),
                'organization_name': request.session.get('organization_name'),
                'start_date': start_date.strftime('%B %d, %Y'),
                'end_date': end_date.strftime('%B %d, %Y'),
                'start_time': request.session.get('start_time'),
                'end_time': request.session.get('end_time'),
                'weekdays': request.session.get('weekdays'),
                'phone': request.session.get('phone'),
                'guestCount': request.session.get('guestCount'),
                'eventDetails': request.session.get('eventDetails'),
                'purpose': request.session.get('purpose'),
                'specialRequirements': request.session.get('specialRequirements'),
                'terms': request.session.get('terms'),
                'matching_dates_count': 0,
                'matching_dates_info': False,
                'selected_weekdays': selected_weekdays,
                'no_matching_dates': True,  
            })

        # Get available venues
        available_venue_response = arnav_check_multiple_week_availability_view(request)

        # Format venues
        formatted_venues = []
        for venue in available_venue_response:
            formatted_venues.append({
                "id": venue.id,
                "name": venue.venue_name,
                "capacity": venue.capacity,
                "facilities": venue.facilities,
                "images": venue.photo_url,
            })

        return render(request, 'request_booking/select_multiple_venues.html', {
            "venues": formatted_venues,
            'eventType': request.session.get('eventType'),
            'fullName': request.session.get('fullName'),
            'email': request.session.get('email'),
            'organization_name': request.session.get('organization_name'),
            'start_date': start_date.strftime('%B %d, %Y'),
            'end_date': end_date.strftime('%B %d, %Y'),
            'start_time': request.session.get('start_time'),
            'end_time': request.session.get('end_time'),
            'weekdays': request.session.get('weekdays'),
            'phone': request.session.get('phone'),
            'guestCount': request.session.get('guestCount'),
            'eventDetails': request.session.get('eventDetails'),
            'purpose': request.session.get('purpose'),
            'specialRequirements': request.session.get('specialRequirements'),
            'terms': request.session.get('terms'),
            'matching_dates_count': len(matching_dates),
            'matching_dates_info': True if matching_dates else False,
            'selected_weekdays': selected_weekdays,
            'no_matching_dates': False,  
        })  
        # Return a simple response (in production, you'd process the data and return appropriate response)
        return HttpResponse("Form data received and printed in console. Check your server logs for details.", 
                          content_type="text/plain")






from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from django.db import transaction
from request_booking.models import CumulativeRequest, Request

import logging
import traceback

from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from django.db import transaction
from request_booking.models import CumulativeRequest, Request

logger = logging.getLogger(__name__)

def cancel_cumulative_request(request):
    if request.method == "POST":
        try:
            print('inside POST cancel_cumulative_request')
            cumulative_request_id = request.POST.get("request_id")
            cancel_reason = request.POST.get("cancel_reason", "No reason provided")

            try:
                print('cumulative_request_id->',cumulative_request_id)
                print('cancel_reason->',cancel_reason)
                cumulative_req = get_object_or_404(CumulativeRequest, cumulative_request_id=cumulative_request_id)
            except Exception as e:
                logger.error(f"Failed to retrieve CumulativeRequest: {e}\n{traceback.format_exc()}")
                messages.error(request, "Failed to retrieve booking information.")
                return redirect('user_dashboard')

            if cumulative_req.user != request.user:
                messages.error(request, "You are not authorized to cancel this booking.")
                return redirect('user_dashboard')

            try:
                individual_requests = Request.objects.filter(
                    cumulative_request_id=cumulative_request_id,
                    status__in=['pending', 'approved']
                )

                if not individual_requests.exists():
                    messages.error(request, "No active or pending requests to cancel.")
                    return redirect('user_dashboard')
            except Exception as e:
                logger.error(f"Failed to retrieve individual requests: {e}\n{traceback.format_exc()}")
                messages.error(request, "An error occurred while retrieving individual requests.")
                return redirect('user_dashboard')

            try:
                with transaction.atomic():
                    for req in individual_requests:
                        req.status = 'user-cancelled'
                        req.reasons = cancel_reason
                        req.save(update_fields=["status", "reasons"])

                        try:
                            booking = req.booking
                            booking.status = 'user-cancelled'
                            booking.save(update_fields=["status"])
                        except Booking.DoesNotExist:
                            pass

                    cumulative_req.status = 'user-cancelled'
                    cumulative_req.reasons = cancel_reason
                    cumulative_req.save(update_fields=["status", "reasons"])

                    # send_cumulative_req_cancellation_email_to_user(cumulative_req, cancel_reason)

                    # send_cumulative_booking_cancelled_by_user_email(cumulative_req)

                    messages.success(request, "Your booking request has been cancelled successfully.")
            except Exception as e:
                logger.error(f"Failed to cancel requests: {e}\n{traceback.format_exc()}")
                messages.error(request, "An error occurred while cancelling your request.")
                return redirect('request_bookinguser_dashboard')

            # return redirect('request_booking:user_dashboard')
            return redirect('faculty_advisor:home')

        except Exception as e:
            logger.error(f"Unexpected error in cancel_cumulative_request: {e}\n{traceback.format_exc()}")
            messages.error(request, "An unexpected error occurred.")
            # return redirect('user_dashboard')
            return redirect('faculty_advisor:home')

    # return redirect('request_booking:user_dashboard')
    return redirect('faculty_advisor:home')








def edit_booking(request):
    if request.method == 'POST':
        print('inside POST edit_booking')
        try:
            # Get cumulative_request_id from the form
            cumulative_request_id = request.POST.get('cumulative_request_id')
            print('cumulative_request_id->',cumulative_request_id)

            # Get updated values from the form
            event_description = request.POST.get('event_description')
            purpose = request.POST.get('purpose')
            guest_count = request.POST.get('guest_count')
            event_type = request.POST.get('event_type')
            additional_info = request.POST.get('additional_info')
            special_requirements = request.POST.get('special_requirements')
            reason_for_approval = request.POST.get('reason_for_approval')
            reason_to_approve = request.POST.get('reason_to_approve')

            # Get CumulativeRequest object
            try:
                cumulative_request = CumulativeRequest.objects.get(cumulative_request_id=cumulative_request_id)
            except CumulativeRequest.DoesNotExist:
                messages.error(request, "Cumulative request not found")
                return redirect('faculty_advisor:home')

            # ✅ Update CumulativeRequest
            print('Update CumulativeRequest')
            cumulative_request.event_details = event_description
            
            cumulative_request.save()
            print('Cumulative Request saved!')

            # ✅ Get all related Request objects
            requests = Request.objects.filter(cumulative_request_id=cumulative_request_id)
            print('requests->',requests)

            for req in requests:
                # Update Request fields
                req.event_details = event_description
                
                req.save()

                # Update corresponding RequestBooking if exists
                try:
                    print('inside try block : Update corresponding RequestBooking if exists')
                    print('before booking_request')
                    booking_request = Booking.objects.get(request_id=req.request_id)
                    print('booking_request->',booking_request)
                    print('event_description->',event_description)
                    booking_request.event_details = event_description
                    print('saving booking request')
                    booking_request.save()
                    print('booking request saved!!')
                except RequestBooking.DoesNotExist:
                    print('inside except block : Update corresponding RequestBooking if exists')
                    # Optional: log or ignore missing RequestBooking
                    continue

            print('Request Purpose updated')

            messages.success(request, "Cumulative booking and related requests updated successfully")
            return redirect('faculty_advisor:home')

        except Exception as e:
            messages.error(request, f"Error updating booking: {str(e)}")
            return redirect('faculty_advisor:home')

    # If not POST request
    return redirect('faculty_advisor:home')

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponse, HttpResponseNotAllowed
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q, F
from datetime import datetime, timedelta
import json
import sys
import traceback
from django.contrib import messages
from threading import Thread

from services import booking_service
from gymkhana.models import Booking
from .models import Venue, Request
from request_booking.models import CumulativeRequest

import uuid


def send_emails_async(email_tasks):
    """
    Send emails in a background thread to prevent request timeout
    """
    def send_all():
        for task in email_tasks:
            try:
                task['function'](**task['kwargs'])
            except Exception as e:
                print(f"Failed to send email: {e}")
    
    thread = Thread(target=send_all)
    thread.daemon = True
    thread.start()

@login_required
def process_multiple_venue_booking(request):
    """
    Handles booking confirmation for multiple venues from the "available venues" page
    """
    if request.method != "POST":
        return redirect("request_booking:request_multiple_week_availability_view")
    
    user = request.user
    if not user.is_authenticated:
        messages.error(request, "You must be logged in to make a booking.")
        return redirect("login")

    try:
        # Get selected venue IDs (now multiple)
        venue_ids = request.POST.getlist("selected_venues")
        
        if not venue_ids:
            messages.error(request, "Please select at least one venue.")
            return redirect("request_booking:request_multiple_week_availability_view")
        
        # Get form data from session (stored from the first form)
        event_type = request.session.get('eventType')
        full_name = request.session.get('fullName')
        email = request.session.get('email', user.email)
        organization_name = request.session.get('organization_name')
        start_date_str = request.session.get('start_date')
        end_date_str = request.session.get('end_date')
        start_time_str = request.session.get('start_time')
        end_time_str = request.session.get('end_time')
        phone_number = request.session.get('phone')
        guest_count = request.session.get('guestCount')
        event_details = request.session.get('eventDetails')
        purpose = request.session.get('purpose', "")
        special_requirements = request.session.get('specialRequirements', "")
        
        # Parse dates and times
        start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()
        end_date = datetime.strptime(end_date_str, "%Y-%m-%d").date()
        
        if end_date < start_date:
            messages.error(request, "End date cannot be before start date.")
            return redirect("request_booking:booking_status")
        
        weekdays = request.session.get('weekdays', [])
        weekdays = sorted([int(day) for day in weekdays])
        
        # Time parsing (you need to import time_str_to_float function)
        start_time = time_str_to_float(start_time_str)
        end_time = time_str_to_float(end_time_str)
        duration = end_time - start_time
        
        # Create a mapping from day names to numbers
        DAY_TO_NUM = {
            'Monday': 0,
            'Tuesday': 1,
            'Wednesday': 2,
            'Thursday': 3,
            'Friday': 4,
            'Saturday': 5,
            'Sunday': 6
        }
        NUM_TO_DAY = {v: k for k, v in DAY_TO_NUM.items()}
        weekday_names = tuple([NUM_TO_DAY[num] for num in weekdays])
        
        total_bookings_created = 0
        total_days = (end_date - start_date).days + 1
        
        # Collect all email tasks to send asynchronously
        email_tasks = []
        
        # Track venues and their results
        venue_results = []  # Will store success/failure info for each venue
        
        # Process each selected venue
        for venue_id in venue_ids:
            try:
                venue = Venue.objects.get(id=venue_id)
                
                # Generate a unique cumulative request ID for this venue
                cumulative_request_id = uuid.uuid4()
                
                venue_bookings_created = 0
                skipped_dates = []  # Track dates that were skipped due to conflicts
                current_date = start_date
                
                # First, collect all valid dates (without conflicts)
                valid_dates = []
                
                # Create individual requests for each matching day
                while current_date <= end_date:
                    if current_date.weekday() in weekdays:
                        # Check for conflicts with existing bookings
                        end_time_for_check = start_time + duration
                        
                        # Check for overlapping bookings on this date/venue
                        conflicts = Request.objects.filter(
                            venue=venue,
                            date=current_date,
                            status__in=['pending', 'approved', 'waiting_for_approval']
                        ).filter(
                            # Check if the time ranges overlap
                            Q(time__lt=end_time_for_check, time__gte=start_time) |  # Existing booking starts during our slot
                            Q(time__lte=start_time + duration, time__gt=start_time)  # Existing booking overlaps our slot
                        )
                        
                        # Also check against confirmed bookings from the Booking model
                        booking_conflicts = Booking.objects.filter(
                            venue_id=venue.id,
                            date=current_date,
                            status__in=['confirmed', 'pending']
                        ).filter(
                            Q(time__lt=end_time_for_check, time__gte=start_time) |
                            Q(time__lte=start_time + duration, time__gt=start_time)
                        )
                        
                        if conflicts.exists() or booking_conflicts.exists():
                            # Skip this date due to conflict
                            print(f"Conflict found for {venue.venue_name} on {current_date} - skipping")
                            skipped_dates.append(current_date.strftime('%Y-%m-%d'))
                        else:
                            # No conflict - add to valid dates
                            valid_dates.append(current_date)
                    
                    current_date += timedelta(days=1)
                
                # Only create cumulative request if we have at least one valid date
                if len(valid_dates) > 0:
                    # Create cumulative request for this venue
                    cumulative_req = CumulativeRequest.objects.create(
                        cumulative_request_id=cumulative_request_id,
                        user=user,
                        full_name=full_name,
                        email=email,
                        phone_number=phone_number,
                        organization_name=organization_name,
                        event_type=event_type,
                        guest_count=guest_count,
                        event_details=event_details,
                        purpose=purpose,
                        special_requirements=special_requirements,
                        venue=venue,
                        start_date=start_date,
                        end_date=end_date,
                        weekdays=",".join([str(day) for day in weekdays]),
                        time=start_time,
                        duration=duration,
                        status='waiting_for_approval'
                    )
                    
                    # Now create individual requests for valid dates
                    for valid_date in valid_dates:
                        new_req = Request.objects.create(
                            user=user,
                            email=email,
                            phone_number=phone_number,
                            full_name=full_name,
                            organization_name=organization_name,
                            event_type=event_type,
                            guest_count=guest_count,
                            additional_info=purpose,
                            date=valid_date,
                            time=start_time,
                            duration=duration,
                            venue=venue,
                            need=organization_name,
                            alternate_venue_1=None,
                            alternate_venue_2=None,
                            event_details=event_details,
                            special_requirements=special_requirements,
                            status='pending',
                            cumulative_booking=True,
                            cumulative_request_id=cumulative_request_id
                        )
                        
                        print(f"Created request for {venue.venue_name} on {valid_date}")
                        venue_bookings_created += 1
                    
                    # Queue emails for async sending
                    email_tasks.append({
                        'function': cumulative_send_confirmation_email_to_requester,
                        'kwargs': {
                            'email': email,
                            'full_name': full_name,
                            'venue_obj': venue,
                            'event_type': event_type,
                            'purpose': purpose,
                            'start_date': start_date,
                            'end_date': end_date,
                            'start_time': start_time,
                            'booking_duration': duration,
                            'weekdays': weekday_names,
                            'total_days': venue_bookings_created
                        }
                    })
                    
                    email_tasks.append({
                        'function': cumulative_send_booking_request_email_to_admin,
                        'kwargs': {
                            'email': venue.venue_admin,
                            'full_name': full_name,
                            'venue_obj': venue,
                            'event_type': event_type,
                            'purpose': purpose,
                            'start_date': start_date,
                            'end_date': end_date,
                            'start_time': start_time,
                            'booking_duration': duration,
                            'weekdays': weekday_names,
                            'total_days': venue_bookings_created
                        }
                    })
                    
                    total_bookings_created += venue_bookings_created
                    
                    # Track success for this venue
                    venue_results.append({
                        'venue_name': venue.venue_name,
                        'success': True,
                        'bookings_created': venue_bookings_created,
                        'skipped_count': len(skipped_dates)
                    })
                    
                    print(f"Created {venue_bookings_created} bookings for {venue.venue_name}")
                    if skipped_dates:
                        print(f"Skipped {len(skipped_dates)} dates for {venue.venue_name} due to conflicts: {', '.join(skipped_dates)}")
                
                else:
                    # All dates had conflicts - don't create cumulative request
                    venue_results.append({
                        'venue_name': venue.venue_name,
                        'success': False,
                        'bookings_created': 0,
                        'skipped_count': len(skipped_dates),
                        'reason': 'All requested dates have conflicting bookings'
                    })
                    print(f"Skipped venue {venue.venue_name} - all {len(skipped_dates)} dates had conflicts")
                
            except Venue.DoesNotExist:
                venue_results.append({
                    'venue_name': f'Venue ID {venue_id}',
                    'success': False,
                    'bookings_created': 0,
                    'skipped_count': 0,
                    'reason': 'Venue not found'
                })
                print(f"Venue with ID {venue_id} not found.")
                continue
            except Exception as e:
                venue_results.append({
                    'venue_name': venue.venue_name if 'venue' in locals() else f'Venue ID {venue_id}',
                    'success': False,
                    'bookings_created': 0,
                    'skipped_count': 0,
                    'reason': f'Error: {str(e)}'
                })
                print(f"Error processing venue {venue_id}: {e}")
                traceback.print_exc()
                continue
        
        # Send all emails asynchronously AFTER database operations are complete
        if email_tasks:
            send_emails_async(email_tasks)
        
        # Provide detailed feedback to user
        successful_venues = [r for r in venue_results if r['success']]
        failed_venues = [r for r in venue_results if not r['success']]
        
        if successful_venues and not failed_venues:
            # All venues succeeded
            messages.success(
                request, 
                f"Successfully created {total_bookings_created} booking request(s) across {len(successful_venues)} venue(s)! Confirmation emails will be sent shortly."
            )
        elif successful_venues and failed_venues:
            # Some succeeded, some failed
            success_msg = f"Successfully created {total_bookings_created} booking request(s) for {len(successful_venues)} venue(s). "
            
            # Build detailed message about partial successes and failures
            venue_details = []
            for r in successful_venues:
                if r['skipped_count'] > 0:
                    venue_details.append(f"{r['venue_name']}: {r['bookings_created']} requests created, {r['skipped_count']} dates skipped due to conflicts")
                else:
                    venue_details.append(f"{r['venue_name']}: {r['bookings_created']} requests created")
            
            for r in failed_venues:
                venue_details.append(f"{r['venue_name']}: Failed - {r['reason']}")
            
            messages.warning(
                request,
                success_msg + " Details: " + "; ".join(venue_details)
            )
        elif not successful_venues and failed_venues:
            # All failed
            failure_details = []
            for r in failed_venues:
                failure_details.append(f"{r['venue_name']}: {r['reason']}")
            
            messages.error(
                request,
                "No bookings were created. " + "; ".join(failure_details)
            )
        else:
            # Shouldn't happen, but just in case
            messages.warning(request, "No bookings were created. Please check availability and try again.")
        
        # Clear session data
        session_keys = [
            'eventType', 'fullName', 'email', 'organization_name',
            'start_date', 'end_date', 'start_time', 'end_time',
            'weekdays', 'phone', 'guestCount', 'eventDetails',
            'purpose', 'specialRequirements', 'terms'
        ]
        for key in session_keys:
            request.session.pop(key, None)
        
        return redirect("request_booking:request_multiple_week_availability_view")
        
    except Exception as e:
        print(f"Error in process_multiple_venue_booking: {e}")
        traceback.print_exc()
        messages.error(request, "An error occurred while processing your booking.")
        return redirect("request_booking:booking_status")

    return redirect("request_booking:request_multiple_week_availability_view")