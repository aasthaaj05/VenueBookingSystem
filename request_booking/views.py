

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



@csrf_exempt  # Disable CSRF protection for testing (remove in production)
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
@csrf_exempt  # Disable CSRF for testing; remove this in production
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
@csrf_exempt
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



    



@csrf_exempt
def book_venue(request):
    print()
    print()
    print("in book_venue func...")
    print()
    print()
    """Handles venue selection and preloads user session details."""
    

    if request.method == "POST":
        print('in book_venue function')
        # venue_name = request.POST.get("venue_name")
        # print(f"Venue selected: {venue_name}")

        # Print session data for debugging
        print("Session Data:", request.session.items())
        print(request.session.get("name"))
        venues = Venue.objects.all()  # Fetch all venues from the database

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

        print(f"Received Form Data: Venue={venue_id}, Event Type={event_type}, Full Name={full_name}, Email={email}, Org={organization_name}")
        print(f"Date={date}, Start Time={start_time}, End Time={end_time}, Phone={phone_number}, Guest Count={guest_count}")
        print(f"Alt Venue 1={alt_venue_1_id}, Alt Venue 2={alt_venue_2_id}, Event Details={event_details}, Purpose={purpose}")

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
                alternate_venue_1=alternate_venue_1,
                alternate_venue_2=alternate_venue_2,
                event_details=event_details,
                guest_count = guest_count,
            )


            

            print(f"Booking Request Created: {booking_request}")
            messages.success(request, "Booking request submitted successfully!")
            return redirect("request_booking:index")  # Redirect to home or bookings list

        except Venue.DoesNotExist:
            print("Error: Invalid venue ID provided.")
            messages.error(request, "Invalid venue selection. Please try again.")
        except ValueError as ve:
            print(f"Error: Invalid date/time format. Exception: {ve}")
            messages.error(request, "Invalid date/time format. Please check and try again.")

    return redirect("request_booking:booking_status")













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
    Dear {venue_obj.department_incharge.name},

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
    venue_incharge_email = venue_obj.department_incharge.email if venue_obj.department_incharge else None
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
    Dear {venue_obj.department_incharge.name},

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
    requests = Request.objects.filter(user_id=user_id).select_related('venue').order_by('-date')

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

