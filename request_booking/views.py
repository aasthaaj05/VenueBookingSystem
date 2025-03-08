

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




def user_dashboard(request):
    if request.method == "GET":
        print("Inside user_dashboard view")
        print("Request path:", request.path)
        print("Request headers:", request.headers)
        print() 
        print()

        # Retrieve stored venue slot availability from the session
        all_slots = request.session.get('all_slots', {})

        print(all_slots)

        # Extract venue names from all_slots
        venue_names = all_slots.keys()

        # Fetch venues from the database
        venues = Venue.objects.filter(venue_name__in=venue_names).values('id', 'venue_name', 'capacity', 'facilities', 'photo_url')

        # Map the venue data with availability
        formatted_venues = []


        for venue in venues:
            venue_name = venue['venue_name']
            formatted_venues.append({
                "id":venue['id'],
                "name": venue_name,
                "capacity": venue['capacity'],
                "facilities": venue['facilities'],  # Assuming it's stored as a list in JSONField
                "images": venue['photo_url'].split(",") if venue['photo_url'] else [],  # Convert CSV string to list
            })

        print()
        print()
        print('----')

        # Pass formatted venue data to the template
        return render(request, 'request_booking/user_dashboard.html', {"venues": formatted_venues})

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
def cancel_request(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Only POST method allowed'}, status=405)

    data = json.loads(request.body)
    req_id = data.get('req_id')
    req_id = req_id.replace('-', '')  # Remove all hyphens


    if not req_id:
        return JsonResponse({'error': 'Missing request ID'}, status=400)

    try:
        result = booking_service.cancelRequest(req_id)
        return JsonResponse({'success': result})
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
            "user_data": user_data  # Passing session data to prefill the form
        })

    if request.method == "GET":
        print("in GET GET book_venue func...")
        # Print session data for debugging
        print("Session Data:", request.session.items())
        print(request.session.get("name"))

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
            "user_data": user_data  # Passing session data to prefill the form
        })






from datetime import datetime
from django.utils.timezone import now  # Handles timezone-aware datetime

@csrf_exempt
def process_booking(request):
    print('process_booking func : request --> ',request)
    """Processes the booking request and saves details in the database."""
    if request.method == "POST":
        print('POST : process_booking func : request --> ',request)
        data = {
            "event_type": request.POST.get("eventType"),
            "other_event_type": request.POST.get("otherEventType"),
            "name": request.session.get("firstName"),  # Full name from session
            "email": request.session.get("email"),  # From session
            "organization_name": request.session.get("organization_name"),  # Fixed typo (extra space)
            "phone": request.POST.get("phone"),
            "venue": request.POST.get("venue"),
            "guest_count": request.POST.get("guestCount"),
            "purpose": request.POST.get("purpose"),
        }
        print(data)

        # Save to database
        venue_obj = Venue.objects.get(venue_name=data["venue"]) if data["venue"] else None
        current_datetime = now()  # Get current date and time

        

        current_time = now().time()
        time_in_hours = current_time.hour  # Extract hour as an integer

        print('in process_booking func : before Request.objects.create')

        print('curr_date : ', now().date())

        current_time = datetime.now()
        formatted_time = current_time.strftime("%Y-%m-%d %H:%M:%S.%f")  # Microseconds included
        print('formatted_time',formatted_time)

        # print('session : ' , request.session)
        print("Session Data (JSON Format):", json.dumps(dict(request.session), indent=4))  # JSON format
        # print("Session Data (Pretty Print):")
        # pprint(dict(request.session))  # Pretty print

        session_dict = json.dumps(dict(request.session))
        print('type of session_dict' , type(session_dict))

        if request.user.role in ['club' , 'fests' , 'student_chapter']:
            status="waiting_for_approval"
        else:
            status="pending"

        '''
        ('club', 'Club'),
        ('fests', 'Fests'),
        ('student_chapter', 'Student Chapter'),
        ('faculty', 'Faculty'),
        ('HOD', 'HOD'),
        ('Dean', 'Dean'),
        ('VC', 'VC'),
        ('Registrar', 'Registrar'),
        ('outsider', 'Outsider'),
        '''

        # booked_date 

        print()
        print()
        print(f""" in process_booking func
            Request.objects.create(
                user={request.user},
                date={request.session.get('start_date')},  # Store current date
                time={request.session.get('start_time')},
                duration={request.session.get("booking_duration")},  
                venue={venue_obj},
                need={data["purpose"]},
                event_details={data["event_type"]},
                status={status},
                created_at={formatted_time},
            )
            """)
        print()
        print()


        Request.objects.create(
            user=request.user,
            date=request.session.get('start_date'),  # Store current date
            # time=time_in_hours,  # Convert time to integer
            time = request.session.get('start_time'),
            duration=request.session.get("booking_duration"),  
            venue=venue_obj,
            need=data["purpose"],
            event_details=data["event_type"],
            status=status,
            created_at = formatted_time,
        )

        print('in process_booking func : after Request.objects.create')

        # return render(request, "request_booking/booking_status.html", {"success": True, "venue": data["venue"]})
        return redirect("/request_booking/booking_status")  
    

    return JsonResponse({"error": "Invalid request"}, status=400)





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
        venue_data.append({
            "id": venue.id,
            "name": venue.venue_name,
            "capacity": venue.capacity,
            "facilities": venue.facilities,  # This is a list (JSONField)
            "images": venue.photo_url.split(',') if venue.photo_url else [],  # Assuming multiple images are comma-separated
        })

    print("VENUE DETAILS:", venue_data)

    context = {
        'venues': venue_data
    }

    return render(request, 'request_booking/user_dashboard.html', context)  # Replace 'your_template.html' with your actual template filename


def index(request):
    return render(request , 'request_booking/index.html')