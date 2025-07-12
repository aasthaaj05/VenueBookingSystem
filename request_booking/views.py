

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
        dates = [req.date.strftime('%Y-%m-%d') for req in individual_requests]

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
        print('clean_weekdays :', clean_weekdays)
        print('weekday_names :', weekday_names)
        print('weekday_str :', weekday_str)



        print("----- Debug Info for CR (Cumulative Request) -----")
        print("Accept:", cr.accept)
        print("Reason to Approve:", cr.reason_to_approve)
        print("Reason to Reject:", cr.reason_to_reject)
        print("Additional Comments:", cr.additional_comments)
        print("Suggest Alternate Venues:", cr.suggest_alternate_venues)
        print("--------------------------------------------------------")

        
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
        print('pending_cumulative_requests : ', pending_cumulative_requests)

    context = {
        'pending_requests': pending_cumulative_requests,
        'person_name': user_obj.name  # Add person_name to context
    }

    return render(request, 'request_booking/cumulative_booking_status.html', context)



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
            start_hour = int(datetime.strptime(start_time_str, "%I:%M %p").strftime("%H"))
            end_hour = int(datetime.strptime(end_time_str, "%I:%M %p").strftime("%H"))

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
            start_time = datetime.strptime(start_time_str, time_format)
            end_time = datetime.strptime(end_time_str, time_format)

            print()
            print()
            print('in ')

            # Calculate duration in hours
            # duration = int((end_time - start_time).total_seconds() // 3600)  # Convert seconds to hours

            duration = int((int(end_hour) - int(start_hour))) 

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



# sender_email = ""  # Outlook Email
# sender_password = "coep"      # Outlook Email Password
# smtp_server = "smtp.office365.com"
# smtp_port = 587  # Outlook SMTP port

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




# def user_dashboard(request, building_name=None):  # Accept building_name
#     if request.method == "GET":
#         print("Inside user_dashboard view")
#         print("Building Name:", building_name)  # Debugging output

#         # Retrieve stored venue slot availability from the session
#         all_slots = request.session.get('all_slots', {})

#         print(all_slots)

#         # Extract venue names from all_slots
#         venue_names = all_slots.keys()

#         # Fetch venues from the database filtered by building_name
#         venues = Venue.objects.filter(venue_name__in=venue_names)

#         if building_name:
#             venues = venues.filter(bui=building_name)  # Filter venues by building

#         venues = venues.values('id', 'venue_name', 'capacity', 'facilities', 'photo_url')

#         # Map the venue data with availability
#         formatted_venues = []

#         for venue in venues:
#             venue_name = venue['venue_name']
#             formatted_venues.append({
#                 "id": venue['id'],
#                 "name": venue_name,
#                 "capacity": venue['capacity'],
#                 "facilities": venue['facilities'],
#                 "images": venue['photo_url'].split(",") if venue['photo_url'] else [],
#             })

#         return render(request, 'request_booking/user_dashboard.html', {
#             "venues": formatted_venues,
#             "building_name": building_name  # Pass building name to template
#         })

#     return HttpResponseNotAllowed(['GET'])

from django.http import HttpResponseNotAllowed
from django.shortcuts import render
from gymkhana.models import Venue

def user_dashboard(request, building_name=None):  # Accept building_name
    if request.method == "GET":
        print("Inside user_dashboard view")
        print("Building Name:", building_name)  # Debugging output

        # # Retrieve stored venue slot availability from the session
        # all_slots = request.session.get('all_slots', {})
        # print(all_slots)

        # Extract venue names from all_slots
        # venue_names = all_slots.keys()

        # Fetch venues from the database filtered by building_name
        # venues = Venue.objects.filter(venue_name__in=venue_names)
        # print('venues : ' , venues)

        # Fetch all venues from the database
        venues = Venue.objects.all()

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
            "start_time": f"{request.session.get('start_time'):02d}:00",  # Convert to HH:MM format
            "end_time": f"{request.session.get('end_time'):02d}:00",  # Convert to HH:MM format
    }

        print('user data : ' , user_data)
        
        return render(request, "request_booking/booking_form.html", {
            "venue": venue_name,
            "user_data": user_data,
            'venues':venues,  # Passing session data to prefill the form
        })






from datetime import datetime
from django.utils.timezone import now  # Handles timezone-aware datetime

# @csrf_exempt
# def process_booking(request):
#     print('process_booking func : request --> ',request)
#     """Processes the booking request and saves details in the database."""
#     if request.method == "POST":
#         print('POST : process_booking func : request --> ',request)
#         data = {
#             "event_type": request.POST.get("eventType"),
#             "other_event_type": request.POST.get("otherEventType"),
#             "name": request.session.get("firstName"),  # Full name from session
#             "email": request.session.get("email"),  # From session
#             "organization_name": request.session.get("organization_name"),  # Fixed typo (extra space)
#             "phone": request.POST.get("phone"),
#             "alternate_venue_1": request.POST.get("alternateVenue1"),
#             "alternate_venue_2": request.POST.get("alternateVenue2"),
#             "venue": request.POST.get("venue"),
#             "guest_count": request.POST.get("guestCount"),
#             "purpose": request.POST.get("purpose"),
#         }
#         print(data)

#         # Save to database
#         venue_obj = Venue.objects.get(venue_name=data["venue"]) if data["venue"] else None
#         alt_venue_1 = Venue.objects.get(id=data["alternate_venue_1"]) if data["alternate_venue_1"] else None
#         alt_venue_2 = Venue.objects.get(id=data["alternate_venue_2"]) if data["alternate_venue_2"] else None

#         current_datetime = now()  # Get current date and time

        

#         current_time = now().time()
#         time_in_hours = current_time.hour  # Extract hour as an integer

#         print('in process_booking func : before Request.objects.create')

#         print('curr_date : ', now().date())

#         current_time = datetime.now()
#         formatted_time = current_time.strftime("%Y-%m-%d %H:%M:%S.%f")  # Microseconds included
#         print('formatted_time',formatted_time)

#         # print('session : ' , request.session)
#         print("Session Data (JSON Format):", json.dumps(dict(request.session), indent=4))  # JSON format
#         # print("Session Data (Pretty Print):")
#         # pprint(dict(request.session))  # Pretty print

#         session_dict = json.dumps(dict(request.session))
#         print('type of session_dict' , type(session_dict))

#         if request.user.role in ['club' , 'fests' , 'student_chapter']:
#             status="waiting_for_approval"
#         else:
#             status="pending"

#         '''
#         ('club', 'Club'),
#         ('fests', 'Fests'),
#         ('student_chapter', 'Student Chapter'),
#         ('faculty', 'Faculty'),
#         ('HOD', 'HOD'),
#         ('Dean', 'Dean'),
#         ('VC', 'VC'),
#         ('Registrar', 'Registrar'),
#         ('outsider', 'Outsider'),
#         '''

#         # booked_date 

#         print()
#         print()
#         print(f""" in process_booking func
#             Request.objects.create(
#                 user={request.user},
#                 date={request.session.get('start_date')},  # Store current date
#                 time={request.session.get('start_time')},
#                 duration={request.session.get("booking_duration")},  
#                 venue={venue_obj},
#                 need={data["purpose"]},
#                 event_details={data["event_type"]},
#                 status={status},
#                 created_at={formatted_time},
#             )
#             """)
#         print()
#         print()

#         checker=Request.objects.filter(user=request.user,
#             date=request.session.get('start_date'),  # Store current date
#             # time=time_in_hours,  # Convert time to integer
#             time = request.session.get('start_time'),
#             duration=request.session.get("booking_duration"),  
#             venue=venue_obj,
#             alternate_venue_1=alt_venue_1,
#             alternate_venue_2=alt_venue_2,
#             need=data["purpose"],
#             event_details=data["event_type"],
#             status=status).exists()
#         if not checker:
#             Request.objects.create(
#                 user=request.user,
#                 date=request.session.get('start_date'),  # Store current date
#                 # time=time_in_hours,  # Convert time to integer
#                 time = request.session.get('start_time'),
#                 duration=request.session.get("booking_duration"),  
#                 venue=venue_obj,
#                 alternate_venue_1=alt_venue_1,
#                 alternate_venue_2=alt_venue_2,
#                 need=data["purpose"],
#                 event_details=data["event_type"],
#                 status=status,
#                 created_at = formatted_time,
#             )
#             send_booking_request_email(request, venue_obj, alt_venue_1, alt_venue_2, data, status , formatted_time)

#             print('in process_booking func : after Request.objects.create')

#         # return render(request, "request_booking/booking_status.html", {"success": True, "venue": data["venue"]})
#         return redirect("/request_booking/booking_status")  
    

#     return JsonResponse({"error": "Invalid request"}, status=400)

from datetime import datetime
import json
from django.http import JsonResponse
from django.shortcuts import redirect
from django.views.decorators.csrf import csrf_exempt
from django.utils.timezone import now  # Handles timezone-aware datetime
from .models import Request, Venue

# @csrf_exempt
# def process_booking(request):
#     if request.method == "POST":
#         print('POST : process_booking func : request --> ', request)

#         # Extracting data from POST request and session
#         data = {
#             "event_type": request.POST.get("eventType"),
#             "other_event_type": request.POST.get("otherEventType"),
#             "name": request.session.get("firstName"),
#             "email": request.session.get("email"),  # Fetch email
#             "phone_number": request.POST.get("phone"),  # Fetch phone number
#             "organization_name": request.session.get("organization_name"),
#             "alternate_venue_1": request.POST.get("alternateVenue1"),
#             "alternate_venue_2": request.POST.get("alternateVenue2"),
#             "venue": request.POST.get("venue"),
#             "guest_count": request.POST.get("guestCount"),
#             "purpose": request.POST.get("purpose"),
#             "additional_info": request.POST.get("additionalInfo"),  # Extra details
#         }

#         print("Received data:", data)

#         # Fetch venue objects
#         venue_obj = Venue.objects.get(venue_name=data["venue"]) if data["venue"] else None
#         alt_venue_1 = Venue.objects.get(id=data["alternate_venue_1"]) if data["alternate_venue_1"] else None
#         alt_venue_2 = Venue.objects.get(id=data["alternate_venue_2"]) if data["alternate_venue_2"] else None

#         # Determine request status based on user role
#         if request.user.role in ['club', 'fests', 'student_chapter']:
#             status = "waiting_for_approval"
#         else:
#             status = "pending"

#         # Checking if a similar request exists
#         checker = Request.objects.filter(
#             user=request.user,
#             date=request.session.get("start_date"),
#             time=request.session.get("start_time"),
#             duration=request.session.get("booking_duration"),
#             venue=venue_obj,
#             alternate_venue_1=alt_venue_1,
#             alternate_venue_2=alt_venue_2,
#             need=data["purpose"],
#             event_details=data["event_type"],
#             status=status,
#             phone_number=data["phone_number"],  # Match phone number
#             email=data["email"],  # Match email
#             additional_info=data["additional_info"],  # Match extra info
#         ).exists()

#         if not checker:
#             # Creating a new request entry
#             booking_request = Request.objects.create(
#                 user=request.user,
#                 date=request.session.get("start_date"),
#                 time=request.session.get("start_time"),
#                 duration=request.session.get("booking_duration"),
#                 venue=venue_obj,
#                 alternate_venue_1=alt_venue_1,
#                 alternate_venue_2=alt_venue_2,
#                 need=data["purpose"],
#                 event_details=data["event_type"],
#                 status=status,
#                 phone_number=data["phone_number"],  # Store phone number
#                 email=data["email"],  # Store email
#                 additional_info=data["additional_info"],  # Store additional info
#             )

#             # Send confirmation email
#             send_booking_request_email(request, venue_obj, alt_venue_1, alt_venue_2, data, status, now())

#             print('Booking request successfully created:', booking_request)

#         return redirect("/request_booking/booking_status")

#     return JsonResponse({"error": "Invalid request"}, status=400)



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
            start_time_obj = datetime.strptime(start_time, "%H:%M").time()
            end_time_obj = datetime.strptime(end_time, "%H:%M").time()

            # Extract only the hour as an integer
            start_time = start_time_obj.hour
            end_time = end_time_obj.hour

            print('start , end time : ',start_time, end_time)  # Example Output: 11, 22
            date_obj = datetime.strptime(date, "%Y-%m-%d").date()

            # Compute the difference
            duration = end_time - start_time

            # Calculate duration in minutes
            # duration = (datetime.combine(date_obj, end_time_obj) - datetime.combine(date_obj, start_time_obj)).seconds // 60
            print(f"Parsed Date: {date_obj}, Start Time: {start_time_obj}, End Time: {end_time_obj}, Duration: {duration} minutes")

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

    return redirect("faculty_advisor:booking_status")

def check_venue_availability_mul_weeks(venue, start_date, num_weeks, weekdays, time, duration):
    # Ensure start_date is a date object, not datetime
    if isinstance(start_date, datetime):
        start_date = start_date.date()

    for week in range(num_weeks):
        week_start = start_date + timedelta(weeks=week)
        for wd in sorted(weekdays):
            # Get the actual date for the weekday in the current week
            day_offset = (wd - week_start.weekday() + 7) % 7
            target_date = week_start + timedelta(days=day_offset)
          # Fetch all active bookings for the venue on the target date. 
            # Iterate through each booking to determine if the requested time slot overlaps with any existing booking.
            # A clash exists if the start time of the requested slot is less than the end time of an existing booking
            # and the end time of the requested slot is greater than the start time of an existing booking.

            existing_bookings = Booking.objects.filter(
                venue=venue,
                date=target_date,
                status='active'
            )
            if (existing_bookings.exists()):
                for booking in existing_bookings:
                    booking_start = booking.time
                    booking_end = booking.time + booking.duration
                    request_start = time
                    request_end = time + duration

                    # Check for overlap
                    if ((request_end >= booking_start and request_start <= booking_end) or (request_start <= booking_end and request_end >= booking_start)):
                        print("detected a conflict")
                        return False
    return True

# @login_required
# def process_booking_multiple(request):
#     if request.method == "POST":
#         print('ojdoepkfvpjeijoj')
#         user = request.user
#         print(f"User: {user}")

#         try:
#             print('in process_booking_multiple()')
#             # Get form data
#             venue_id = request.POST.get("venue")
#             venue = Venue.objects.get(id=venue_id)

#             event_type = request.POST.get("eventType")
#             full_name = request.POST.get("fullName")
#             email = request.POST.get("email", user.email)
#             organization_name = request.POST.get("organization_name")
#             start_date_str = request.POST.get("start_date_str")
#             start_time_str = request.POST.get("start_time_str")
#             end_time_str = request.POST.get("end_time_str")
#             phone_number = request.POST.get("phone_number")
#             guest_count = request.POST.get("guest_count")
#             event_details = request.POST.get("event_details")
#             purpose = request.POST.get("purpose", "")
#             special_requirements = request.POST.get("specialRequirements", "")
#             num_weeks = int(request.POST.get("num_weeks", 1))
#             weekdays = request.POST.getlist("weekdays")  # Should be list of strings like ["0", "2", "4"]

#             # Debug: Print all values and their types
#             print("venue_id:", venue_id, "| type:", type(venue_id))
#             print("venue:", venue, "| type:", type(venue))
#             print("event_type:", event_type, "| type:", type(event_type))
#             print("full_name:", full_name, "| type:", type(full_name))
#             print("email:", email, "| type:", type(email))
#             print("organization_name:", organization_name, "| type:", type(organization_name))
#             print("start_date_str:", start_date_str, "| type:", type(start_date_str))
#             print("start_time_str:", start_time_str, "| type:", type(start_time_str))
#             print("end_time_str:", end_time_str, "| type:", type(end_time_str))
#             print("phone_number:", phone_number, "| type:", type(phone_number))
#             print("guest_count:", guest_count, "| type:", type(guest_count))
#             print("event_details:", event_details, "| type:", type(event_details))
#             print("purpose:", purpose, "| type:", type(purpose))
#             print("special_requirements:", special_requirements, "| type:", type(special_requirements))
#             print("num_weeks:", num_weeks, "| type:", type(num_weeks))
#             print("weekdays:", weekdays, "| type:", type(weekdays))


#             print(f"weekdays (raw): {weekdays}")
#             weekdays = sorted([int(day) for day in weekdays])
#             print(f"Parsed weekdays: {weekdays}")
#             print('098mwo9hyn')

#             # Time parsing
#             # start_time = datetime.strptime(start_time_str, "%H:%M").time().hour
#             # end_time = datetime.strptime(end_time_str, "%H:%M").time().hour
#             start_time = int(start_time_str)
#             print('4444')
#             end_time = int(end_time_str)
#             print('2222')
#             duration = end_time - start_time
#             print('1111')
#             start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()
#             print('poeri0i0i0')

#             created_count = 0

#             if (check_venue_availability_mul_weeks(venue, start_date, num_weeks, weekdays, start_time, duration) == False):
#                 return redirect('faculty_advisor:home')

            


#             # Create the Cumulative Request first
#             cumulative_request = CumulativeRequest.objects.create(
#                 user=user,
#                 email=email,
#                 phone_number=phone_number,
#                 full_name=full_name,
#                 organization_name=organization_name,
#                 event_type=event_type,
#                 guest_count=guest_count,
#                 additional_info=purpose,
#                 event_details=event_details,
#                 purpose=purpose,
#                 start_date=start_date,
#                 weekdays=",".join(map(str, weekdays)),  # Store as comma-separated string
#                 time=start_time,
#                 duration=duration,
#                 num_weeks=num_weeks,
#                 venue=venue,
#                 special_requirements=special_requirements,
#                 status='pending'
#             )

#             individual_requests = []
#             for week in range(num_weeks):
#                 week_start = start_date + timedelta(weeks=week)
#                 for weekday in weekdays:
#                     offset = (weekday - week_start.weekday() + 7) % 7
#                     current_date = week_start + timedelta(days=offset)

#                     # Create the Request with reference to cumulative_request
#                     new_req = Request.objects.create(
#                         user=user,
#                         email=email,
#                         phone_number=phone_number,
#                         full_name=full_name,
#                         organization_name=organization_name,
#                         event_type=event_type,
#                         guest_count=guest_count,
#                         additional_info=purpose,
#                         date=current_date,
#                         time=start_time,
#                         duration=duration,
#                         venue=venue,
#                         need=organization_name,
#                         alternate_venue_1=None,
#                         alternate_venue_2=None,
#                         event_details=event_details,
#                         special_requirements=special_requirements,
#                         status='pending',
#                         cumulative_request_id=cumulative_request.cumulative_request_id,
#                         cumulative_booking=True
#                     )

#                     individual_requests.append(new_req)
#                     print(f"Created request for {current_date}")
#                     created_count += 1

            

#             if created_count:
#                 messages.success(request, f"{created_count} booking request(s) submitted successfully!")
#             else:
#                 messages.warning(request, "No requests were created (conflicts or duplicates).")

#             return redirect("faculty_advisor:home")

#         except Venue.DoesNotExist:
#             print("Invalid venue.")
#             messages.error(request, "Invalid venue selected.")
#         except ValueError as ve:
#             print(f"ValueError: {ve}")
#             messages.error(request, "Invalid input. Please check your form.")

#         return redirect("request_booking:booking_status")
#     else:
#         venues = Venue.objects.all()
#         print("heherer ewrewrhewjwhrjwh in request multiple")
#         return render(request, "request_booking/check_multiple_week_avail.html", {"venues": venues})



def cumulative_send_confirmation_email_to_requester(email, full_name, venue_obj, event_type, purpose, start_date, start_time, booking_duration , num_week , weekdays):
    print()
    print('---------in send_confirmation_email_to_requester()------')
    print(f'Requester email: {email}')
    print()
    print()
    print('---------in cumulative_send_confirmation_email_to_requester()------')
    print(f"email: {email} (type: {type(email).__name__})")
    print(f"full_name: {full_name} (type: {type(full_name).__name__})")
    print(f"venue_obj: {venue_obj} (type: {type(venue_obj).__name__})")
    print(f"venue_obj.venue_name: {getattr(venue_obj, 'venue_name', 'N/A')}")
    print(f"event_type: {event_type} (type: {type(event_type).__name__})")
    print(f"purpose: {purpose} (type: {type(purpose).__name__})")
    print(f"start_date: {start_date} (type: {type(start_date).__name__})")
    print(f"start_time: {start_time} (type: {type(start_time).__name__})")
    print(f"booking_duration: {booking_duration} (type: {type(booking_duration).__name__})")
    print(f"num_week: {num_week} (type: {type(num_week).__name__})")
    print(f"weekdays: {weekdays} (type: {type(weekdays).__name__})")
    print()


    if not email:
        print("Requester email not found.")
        return

    # Format current timestamp
    formatted_time = datetime.now().strftime('%d-%m-%Y %I:%M %p')

    # Email content
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = email
    msg['Subject'] = "Your Venue Booking Request Has Been Initiated"

    body = f"""
    Dear {full_name},

    Your venue booking request has been successfully initiated.

    Request Details:
    - Venue: {venue_obj.venue_name}
    - Date: {start_date}
    - Time: {start_time}
    - Duration: {booking_duration} hours
    - Number of Weeks : {num_week}
    - Weekdays : {weekdays}
    - Purpose: {purpose}
    - Event Type: {event_type}
    - Status: Initiated
    - Requested At: {formatted_time}

    We will notify you once your request is reviewed by the venue admin.

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

        print(f"Confirmation email sent to requester: {email}")
    except Exception as e:
        print(f"Failed to send email to {email}: {e}")

    print('---------Ended ---- send_confirmation_email_to_requester()------')


def cumulative_send_booking_request_email_to_admin(email, full_name, venue_obj, event_type, purpose,
                                                   start_date, start_time, booking_duration,
                                                   num_week, weekdays):
    print()
    print('---------in cumulative_send_booking_request_email_to_admin()------')
    
    try:
        # Debug prints
        print(f"Admin email: {email} (type: {type(email).__name__})")
        print(f"Admin full_name: {full_name} (type: {type(full_name).__name__})")
        print(f"venue_obj: {venue_obj} (type: {type(venue_obj).__name__})")
        print(f"venue_obj.venue_name: {getattr(venue_obj, 'venue_name', 'N/A')}")
        print(f"event_type: {event_type} (type: {type(event_type).__name__})")
        print(f"purpose: {purpose} (type: {type(purpose).__name__})")
        print(f"start_date: {start_date} (type: {type(start_date).__name__})")
        print(f"start_time: {start_time} (type: {type(start_time).__name__})")
        print(f"booking_duration: {booking_duration} (type: {type(booking_duration).__name__})")
        print(f"num_week: {num_week} (type: {type(num_week).__name__})")
        print(f"weekdays: {weekdays} (type: {type(weekdays).__name__})")
        print()

        if not email:
            print("Admin email not found.")
            return

        # Format current timestamp
        formatted_time = datetime.now().strftime('%d-%m-%Y %I:%M %p')

        # Compose email
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = venue_obj.venue_admin
        msg['Subject'] = "New Venue Booking Request Initiated"

        body = f"""
Dear {full_name},

A new venue booking request has been initiated and requires your review.

Request Details:
- Venue: {venue_obj.venue_name}
- Date: {start_date}
- Time: {start_time}
- Duration: {booking_duration} hours
- Number of Weeks: {num_week}
- Weekdays: {weekdays}
- Purpose: {purpose}
- Event Type: {event_type}
- Status: Pending
- Requested At: {formatted_time}

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

        print(f"Booking request email sent to venue admin: {email}")

    except Exception as e:
        print(f"Failed to send booking request email: {e}")

    print('---------Ended ---- cumulative_send_booking_request_email_to_admin()------')



@login_required
def process_booking_multiple(request):
    print('---process_booking_multiple---\n\n\n')
    if request.method == "POST":
       
        print('---POST yyy process_booking_multiple---\n\n\n')

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
            print(ss)
            print(ss)
            print('[[[[[[[[[]]]]]]]]]')
            print('[[[[[[[[[]]]]]]]]]')
            print('[[[[[[[[[]]]]]]]]]')
            print('[[[[[[[[[]]]]]]]]]')
            print('[[[[[[[[[]]]]]]]]]')
            print('[[[[[[[[[]]]]]]]]]')
            print('[[[[[[[[[]]]]]]]]]')
            num_weeks = int(request.POST.get("num_weeks", 1))
            weekdays = request.POST.getlist("weekdays")  # Should be list of strings like ["0", "2", "4"]

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
            print(f"num_weeks: {num_weeks} (type: {type(num_weeks).__name__})")
            print(f"weekdays: {weekdays} (type: {type(weekdays).__name__})")

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
            # start_time = datetime.strptime(start_time_str, "%H:%M").time().hour
            # end_time = datetime.strptime(end_time_str, "%H:%M").time().hour
            start_time = int(start_time_str)
            end_time = int(end_time_str)
            duration = end_time - start_time
            start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()
            # start_date = int(start_date_str)
            # end_date = datetime.strptime(end_date_str, "%Y-%m-%d").date()

            created_count = 0

            if (check_venue_availability_mul_weeks(venue, start_date, num_weeks, weekdays, start_time, duration) == False):
                return redirect('faculty_advisor:home')

            # Generate a unique cumulative request ID
            cumulative_request_id = uuid.uuid4()

            event_type = request.session.get('eventType')
            print('event_type : ', event_type)


            # ✅ Create CumulativeRequest entry
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
                num_weeks=num_weeks,
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
            

            for week in range(num_weeks):
                week_start = start_date + timedelta(weeks=week)
                for weekday in weekdays:
                    mail_start_time = start_time
                    mail_duration = duration

                    # weekday_num = DAY_TO_NUM[weekday]
                    # print('weekday_num : ', weekday_num)
                    offset = (weekday - week_start.weekday() + 7) % 7
                    current_date = week_start + timedelta(days=offset)

                    print('------')
                    print('current_date : ' , current_date)
                    print('----')

                    # Create the Request
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
                        cumulative_booking=True,  # This is for type2
                        cumulative_request_id=cumulative_request_id  # Assign the same ID for all requests
                    )

                    print(f"Created request for {current_date}")
                    created_count += 1

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
                    num_week = num_weeks,
                    weekdays = weekday_names,
                )
            except Exception as e:
                print(f"Failed to send confirmation email to requester: {e}")

            try:
                cumulative_send_booking_request_email_to_admin(email=email,
                    full_name=full_name,
                    venue_obj=venue,
                    event_type=event_type,
                    purpose=purpose,
                    start_date=start_date,
                    start_time=mail_start_time,
                    booking_duration=mail_duration,  # Update this if your logic has actual duration
                    num_week = num_weeks,
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

from datetime import datetime, timedelta
from django.utils.timezone import make_aware
from django.db.models import Q
import calendar




def check_multiple_week_availability_view(request):
    if request.method == 'POST':
        try:
            start_date_str = request.POST.get("start_date")
            num_weeks = int(request.POST.get("num_weeks"))
            weekdays = request.POST.getlist("weekdays")

            # Convert inputs
            start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()
            weekdays = [int(day) for day in weekdays]

            venues = Venue.objects.all()

            available_venues = []
            user=request.user
            # event_type = request.POST.get("eventType")
            # full_name = request.POST.get("fullName")
            # email = request.POST.get("email", user.email)
            # organization_name = request.POST.get("organization_name")
            start_time_str = request.POST.get("start_time")
            end_time_str = request.POST.get("end_time")
            # phone_number = request.POST.get("phone")
            # guest_count = request.POST.get("guestCount")
            # event_details = request.POST.get("eventDetails")
            # purpose = request.POST.get("purpose", "")
            # special_requirements = request.POST.get("specialRequirements", "")
            start_hour = datetime.strptime(start_time_str, "%H:%M").time().hour
            end_hour = datetime.strptime(end_time_str, "%H:%M").time().hour
            duration = int((int(end_hour) - int(start_hour)))
            # Debugging output
            print(f"Start Date: {start_date}")
            print(f"Number of Weeks: {num_weeks}")
            print(f"Start Time: {start_time_str}")
            print(f"End Time: {end_time_str}")
            print(f"Weekdays: {weekdays}")
            # print(f"Guest Count: {guest_count}")
            # print(f"Event Details: {event_details}")
            # print(f"Purpose: {purpose}")
            # print(f"Special Requirements: {special_requirements}")
            for venue in venues:
            # Call the check function
                is_available = check_venue_availability_mul_weeks(
                    venue=venue,
                    start_date=start_date,
                    num_weeks=num_weeks,
                    weekdays=weekdays,
                    time=int(start_hour),
                    duration=duration,
                )
                if is_available:
                    available_venues.append(venue)

            print("venues available:", available_venues)

            return JsonResponse({
                "status": "success",
                "venues": available_venues,
            })

        except Exception as e:
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

    A new venue booking request has been initiated.

    Request Details:
    - Requested by: {request.user.name} ({request.user.email})
    - Venue: {venue_obj.venue_name}
    - Date: {start_date}
    - Time: {start_time}
    - Duration: {booking_duration} hours
    - Purpose: {purpose}
    - Event Type: {event_type}
    - Alternate Venue 1: {alt_venue_1.venue_name if alt_venue_1 else 'None'}
    - Alternate Venue 2: {alt_venue_2.venue_name if alt_venue_2 else 'None'}
    - Status: Pending
    - Requested At: {formatted_time}


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

def send_booking_request_email(request, venue_obj, alt_venue_1, alt_venue_2, event_type,purpose , formatted_time):
    # Get venue in-charge email
    # venue_incharge_email = venue_obj.department_incharge.email if venue_obj.department_incharge else None
    venue_incharge_email = venue_obj.venue_admin if venue_obj.venue_admin else None
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
    Dear ,

    A new venue booking request has been submitted.

    Request Details:
    - Requested by: {request.user.name} ({request.user.email})
    - Venue: {venue_obj.venue_name}
    - Date: {start_date}
    - Time: {start_time}
    - Duration: {booking_duration} hours
    - Purpose: {purpose}
    - Event Type: {event_type}
    - Alternate Venue 1: {alt_venue_1.venue_name if alt_venue_1 else 'None'}
    - Alternate Venue 2: {alt_venue_2.venue_name if alt_venue_2 else 'None'}
    - Status: Pending
    - Requested At: {formatted_time}

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
    print()
    print()
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

    print('in booking status function')
    print()
    print()
    print('requests : ', requests)
    print('preseon name : ' , person_name)
    print()
    print()
    

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




# def cancel_booking(request):
#     if request.method == 'POST':
#         request_id = request.POST.get('request_id')
#         cancel_reason = request.POST.get('cancel_reason')
        
#         try:
#             # Get the booking request
#             booking = BookingRequest.objects.get(request_id=request_id, user=request.user)
            
#             # Update the status and save reason
#             booking.status = 'cancelled'
#             booking.cancellation_reason = cancel_reason
#             booking.save()
            
#             messages.success(request, 'Booking has been cancelled successfully.')
#             return redirect('bookings')  # Redirect to your bookings page
            
#         except BookingRequest.DoesNotExist:
#             messages.error(request, 'Booking not found or you are not authorized to cancel it.')
#             return redirect('bookings')
    
#     # If not POST, redirect back
#     return redirect('request_booking/booking_status')







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
    - Time: {event_time}:00 hrs
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












# def cancel_booking(request):
#     print()
#     print()
#     print('---cancel_booking()---')
#     print()
#     print()
#     if request.method == 'POST':
#         request_id = request.POST.get('request_id')
#         cancel_reason = request.POST.get('cancel_reason')

#         print("cancel_reason : " , cancel_reason)
#         print()
#         print()
#         print('---cancel_booking()---')
#         print('---cancel_booking()---')
#         print('---cancel_booking()---')
#         print('---cancel_booking()---')
        
#         try:
#             # Get the booking
#             booking = Booking.objects.get(request__request_id=request_id, user=request.user)

#             # Check if status is either 'approved' or 'pending'
#             if booking.request.status not in ['approved', 'pending']:
#                 print("booking.status not in [approved, pending]")
#                 messages.error(request, f'Only bookings with status "approved" or "pending" can be cancelled. Current status: {booking.status}')
#                 return redirect('/request_booking/booking_status')
            
#             # Cancel the booking
#             booking.status = 'user-cancelled'
#             booking.msg = cancel_reason  # If you want to store user comment
#             booking.save()

#             # Also update the corresponding request status to 'user-cancelled'
#             booking.request.status = 'user-cancelled'
#             booking.request.reasons = cancel_reason  # Store the reason if needed
#             booking.request.save()

#             send_cancellation_email_to_user(
#                 user_email=booking.user.email,
#                 user_name=booking.user.name,
#                 venue_name=booking.venue.venue_name,
#                 event_date=booking.date,
#                 event_time=booking.time,
#                 cancel_reason=cancel_reason
#             )
#             print('mail donemail donemail donemail donemail donemail done')

#             messages.success(request, 'Booking has been cancelled successfully.')
#             return redirect('/request_booking/booking_status')  # Replace with your actual redirect target

#         except Booking.DoesNotExist:
#             messages.error(request, 'Booking not found or you are not authorized to cancel it.')
#             return redirect('/request_booking/booking_status')  # Replace with your actual redirect target
    
#     # If not POST, redirect back
#     return redirect('/request_booking/booking_status')


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


def arnav_check_multiple_week_availability_view(request):
    if request.method == 'POST':
        
        print('POST check_multiple_week_availability_view')
        start_date_str = request.POST.get("start_date")
        num_weeks = int(request.POST.get("num_weeks"))
        weekdays = request.POST.getlist("weekdays")

        # Convert inputs
        start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()
        weekdays = [int(day) for day in weekdays]

        venues = Venue.objects.all()

        available_venues = []
        user=request.user
            # event_type = request.POST.get("eventType")
            # full_name = request.POST.get("fullName")
            # email = request.POST.get("email", user.email)
            # organization_name = request.POST.get("organization_name")
        start_time_str = request.POST.get("start_time")
        print("1")
        end_time_str = request.POST.get("end_time")
        print("2")
        phone_number = request.POST.get("phone")
        print("3")
        guest_count = request.POST.get("guestCount")
        print("4")
        event_details = request.POST.get("eventDetails")
        print("5")
        purpose = request.POST.get("purpose", "")
        print("6")
        special_requirements = request.POST.get("specialRequirements", "")
        print("7")
        # start_hour = datetime.strptime(start_time_str, "%H:%M").time().hour
        start_hour = int(start_time_str)
        print("8")
        # end_hour = datetime.strptime(end_time_str, "%H:%M").time().hour
        end_hour = int(end_time_str)
        print("9")
        duration = int((int(end_hour) - int(start_hour)))
        print("10")
        # Debugging output
        print(f"Start Date: {start_date}")
        print(f"Number of Weeks: {num_weeks}")
        print(f"Start Time: {start_time_str}")
        print(f"End Time: {end_time_str}")
        print(f"Weekdays: {weekdays}")
        print(f"Guest Count: {guest_count}")
        print(f"Event Details: {event_details}")
        print(f"Purpose: {purpose}")
        print(f"Special Requirements: {special_requirements}")
        
        for venue in venues:
            # Call the check function
            is_available = check_venue_availability_mul_weeks(
                venue=venue,
                start_date=start_date,
                num_weeks=num_weeks,
                weekdays=weekdays,
                time=int(start_hour),
                duration=duration,
            )
            if is_available:
                available_venues.append(venue)

        print("venues available:", available_venues)

            # return JsonResponse({
            #     "status": "success",
            #     "venues": available_venues,
            # })
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
        # Convert venues queryset to proper format
        # venue_list = []
        # for venue in venues:
        #     venue_dict = {
        #         'id': venue.id,
        #         'name': str(venue.venue_name),  # Ensure this is a string
        #         'capacity': venue.capacity,
        #         'facilities': venue.facilities,
        #         'images': []  # Add proper image handling if needed
        #     }
        #     venue_list.append(venue_dict)

        print("heherer ewrewrhewjwhrjwh in request multiple")
        print('venues : ', venues)
        # print('venue_list : ', venue_list)
        # Fetch user details from session
        user_data = {
            "name": request.session.get("name"),  # Full name from session
            "email": request.session.get("email"),
            "organization_name": request.session.get("organization_name"),
            "date": request.session.get("start_date"),  # Extracting start date
            "start_time": request.session.get("start_time"),  # Extracting start time
            "end_time": request.session.get("end_time"),  # Extracting end time
        }

        print('user_data : ', user_data)
        return render(request, "request_booking/check_multiple_week_avail.html", {"venue_list": venues, "user_data":user_data})

    def post(self, request, *args, **kwargs):
        print('in RequestMultipleWeekAvailabilityView POST')
        # Print all form data for debugging
        available_venue_response = arnav_check_multiple_week_availability_view(request)
        print("\n" + "="*50)
        print('available_venue_response : ',available_venue_response)
        print('type(available_venue_response) : ',type(available_venue_response))
        print('type(available_venue_response[0]) : ',type(available_venue_response[0]))
        print()
        print()
        print("DEBUG: FORM DATA RECEIVED")
        print("="*50)
        
        # Print POST data
        print("\nPOST Data:")
        pprint.pprint(request.POST.dict())
        
        # Print individual fields
        print("\nIndividual Fields:")
        print(f"Venue ID: {request.POST.get('venue')}")
        print(f"Event Type: {request.POST.get('eventType')}")
        print(f"Full Name: {request.POST.get('fullName')}")
        print(f"Email: {request.POST.get('email')}")
        print(f"Organization: {request.POST.get('organization_name')}")
        print(f"Start Date: {request.POST.get('start_date')}")
        print(f"Start Time: {request.POST.get('start_time')}")
        print(f"End Time: {request.POST.get('end_time')}")
        print(f"Number of Weeks: {request.POST.get('num_weeks')}")
        print(f"Selected Weekdays: {request.POST.getlist('weekdays')}")
        print(f"Phone: {request.POST.get('phone')}")
        print(f"Guest Count: {request.POST.get('guestCount')}")
        print(f"Event Details: {request.POST.get('eventDetails')}")
        print(f"Purpose: {request.POST.get('purpose')}")
        print(f"Special Requirements: {request.POST.get('specialRequirements')}")
        print(f"Terms Accepted: {request.POST.get('terms')}")

        # Store form data in session
        request.session['venue'] = request.POST.get('venue')
        request.session['eventType'] = request.POST.get('eventType')
        request.session['fullName'] = request.POST.get('fullName')
        request.session['email'] = request.POST.get('email')
        request.session['organization_name'] = request.POST.get('organization_name')
        request.session['start_date'] = request.POST.get('start_date')
        request.session['start_time'] = request.POST.get('start_time')
        request.session['end_time'] = request.POST.get('end_time')
        request.session['num_weeks'] = request.POST.get('num_weeks')
        request.session['weekdays'] = request.POST.getlist('weekdays')  # Store list as is
        request.session['phone'] = request.POST.get('phone')
        request.session['guestCount'] = request.POST.get('guestCount')
        request.session['eventDetails'] = request.POST.get('eventDetails')
        request.session['purpose'] = request.POST.get('purpose')
        request.session['specialRequirements'] = request.POST.get('specialRequirements')
        request.session['terms'] = request.POST.get('terms')

        # Optional: Save session explicitly (Django does this automatically when modified)
        request.session.modified = True

        
        print("\n" + "="*50 + "\n")

        # Map the venue data with availability
        formatted_venues = []

        for venue in available_venue_response:
            venue_name = venue.venue_name,
            formatted_venues.append({
                "id": venue.id,
                "name": venue_name,
                "capacity": venue.capacity,
                "facilities": venue.facilities,
                "images": venue.photo_url,
            })

        print('formatted_venu es : ', formatted_venues)
        print('---------')
        print('---------')
        print('---------')
        # Debug: Print all session values and their types
        debug_keys = [
            'eventType', 'fullName', 'email', 'organization_name', 'start_date',
            'start_time', 'end_time', 'num_weeks', 'weekdays', 'phone',
            'guestCount', 'eventDetails', 'purpose', 'specialRequirements', 'terms'
        ]

        print("=== Session Data Debug ===")
        for key in debug_keys:
            value = request.session.get(key)
            print(f"{key}: {value} | type: {type(value)}")
        print("==========================")

        

        return render(request, 'request_booking/book_multiple_venues.html', {
            "venues": formatted_venues,
            # "building_name": building_name  # Pass building name to template
            'eventType': request.session.get('eventType'),
            'fullName': request.session.get('fullName'),
            'email': request.session.get('email'),
            'organization_name': request.session.get('organization_name'),
            'start_date': request.session.get('start_date'),
            'start_time': request.session.get('start_time'),
            'end_time': request.session.get('end_time'),
            'num_weeks': request.session.get('num_weeks'),
            'weekdays': request.session.get('weekdays'),
            'phone': request.session.get('phone'),
            'guestCount': request.session.get('guestCount'),
            'eventDetails': request.session.get('eventDetails'),
            'purpose': request.session.get('purpose'),
            'specialRequirements': request.session.get('specialRequirements'),
            'terms': request.session.get('terms'),
        })
        
        # Return a simple response (in production, you'd process the data and return appropriate response)
        return HttpResponse("Form data received and printed in console. Check your server logs for details.", 
                          content_type="text/plain")