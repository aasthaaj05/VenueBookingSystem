from django.shortcuts import render

# Create your views here.

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from services import booking_service

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


from django.http import JsonResponse
from django.db.models import Q
from datetime import datetime, timedelta
from .models import Venue





from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from datetime import datetime, timedelta
from .models import  Venue
from gymkhana.models import Booking



from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from .models import Venue

@csrf_exempt  # Disable CSRF protection for testing (remove in production)
def get_available_slots(request):
    if request.method == "POST":
        try:
            print('Request received:', request)

            # Parse JSON data from request body
            data = json.loads(request.body.decode("utf-8"))  # Correct way to parse JSON

            print("Received Data:", data)

            # Extract start_date from request data
            start_date = data.get("date")
            end_date = data.get("end_date", start_date)  # Default end_date to start_date if missing

            print(f"Start Date: {start_date}, End Date: {end_date}")

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

            print('1111111111111111')

                # return JsonResponse({
                #     "message": "Booking successful", 
                #     "redirect_url": "/request_booking/user_dashboard"
                # })
            # return redirect('/users/login')  # Redirect to new page

            return JsonResponse({
                "message": "Booking successful",
                "redirect_url": "/request_booking/user_dashboard"
            })
            
            # return redirect('/users/home')
                # return render()
                # return render(request, 'venues.html', {'venues': venues})
                # return render(request, 'request_booking/user_dashboard.html', {'all_slots': all_slots})
                # return render(request, 'request_booking/user_dashboard.html')


        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON format"}, status=400)

        return JsonResponse({"error": "Invalid request method"}, status=405)





from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt

# Sample venue data (Replace with database queries)
venues = [
    {
        "name": "Grand Hall",
        "capacity": 500,
        "facilities": ["Parking", "Stage", "Lighting"],
        "images": ["/static/images/hall1.jpg", "/static/images/hall2.jpg"]
    },
    {
        "name": "Conference Room",
        "capacity": 150,
        "facilities": ["Projector", "AC", "Wifi"],
        "images": ["/static/images/room1.jpg", "/static/images/room2.jpg"]
    }
]

def venue_list(request):
    return render(request, 'venues.html', {'venues': venues})



@csrf_exempt
def book_venue(request):
    if request.method == "POST":
        venue_name = request.POST.get("venue_name")
        # Process the booking logic here (e.g., save to the database)
        return redirect('venue_list')  # Redirect back to venue list
    


from django.shortcuts import render

from django.shortcuts import render
from django.http import HttpResponseNotAllowed

# def user_dashboard(request):
#     if request.method == "GET":  # Ensuring only GET requests are processed
#         print('444444444444')  # Debugging
#         return render(request, 'request_booking/user_dashboard.html')
#     else:
#         return HttpResponseNotAllowed(['GET'])  # Return 405 Method Not Allowed for other methods

import sys
from django.http import HttpResponse

import traceback

from django.http import HttpResponse

# def user_dashboard(request):
#     if request.method == "GET":
#         print("Inside user_dashboard view", flush=True)
#         return HttpResponse("<h1>User Dashboard Loaded</h1>")  # Simple response
#     else:
#         return HttpResponseNotAllowed(['GET'])


def f(a,b):
    return a+b

# def user_dashboard(request):
#     if request.method == "GET": 
#         print("Inside user_dashboard view")
#         print("Request path:", request.path)
#         print("Request headers:", request.headers)  # Check if a redirect caused this
#         print('ooooooooooooooooooooo')
#         print(f(1,2))



#         # return HttpResponse("<h1>User Dashboarlkjsaldjadaod Loaded</h1>")
#         return render(request, 'request_booking/user_dashboard.html')
        
#     else:
#         return HttpResponseNotAllowed(['GET'])



from django.shortcuts import render
from django.http import HttpResponseNotAllowed

def user_dashboard(request):
    if request.method == "GET":
        print("Inside user_dashboard view")
        print("Request path:", request.path)
        print("Request headers:", request.headers)
        print('ooooooooooooooooooooo')

        # Store in session to access in the next view
        all_slots = request.session['all_slots'] 

        print(all_slots)

        venues = [
            {
                "name": "Grand Hall",
                "capacity": 500,
                "facilities": ["Parking", "Stage", "Lighting"],
                "images": ["/static/images/hall1.jpg", "/static/images/hall2.jpg"]
            },
            {
                "name": "Conference Room",
                "capacity": 150,
                "facilities": ["Projector", "AC", "Wifi"],
                "images": ["/static/images/room1.jpg", "/static/images/room2.jpg"]
            }
        ]

        return render(request, 'request_booking/user_dashboard.html', {"venues": venues})

    return HttpResponseNotAllowed(['GET'])




# def user_dashboard(request):
#     if request.method == "GET":
#         print("Inside user_dashboard view")
#         print("Request path:", request.path)
#         print("Request headers:", request.headers)
#         print('ooooooooooooooooooooo')

#         # Store in session to access in the next view
#         all_slots = request.session['all_slots'] 

#         print(all_slots)
        
        

#         return render(request, 'request_booking/user_dashboard.html', {"venues": venues})

#     return HttpResponseNotAllowed(['GET'])

from django.shortcuts import render
from django.http import HttpResponseNotAllowed
from gymkhana.models import Venue  # Replace 'your_app' with your actual app name

# def user_dashboard(request):
#     if request.method == "GET":
#         print("Inside user_dashboard view")
#         print("Request path:", request.path)
#         print("Request headers:", request.headers)
#         print('ooooooooooooooooooooo')

#         # Retrieve stored venue slot availability from the session
#         all_slots = request.session.get('all_slots', {})

#         print(all_slots)

#         # Extract venue names from all_slots
#         venue_names = all_slots.keys()

#         # Fetch venues from the database
#         venues = Venue.objects.filter(venue_name__in=venue_names).values('venue_name', 'capacity', 'facilities')

#         # Map the venue data with availability
#         mapped_venues = {}

#         for venue in venues:
#             print('venue : ' , venue)
#             venue_name = venue['venue_name']
#             mapped_venues[venue_name] = {
#                 'capacity': venue['capacity'],
#                 'facilities': venue['facilities'],
#                 'availability': all_slots.get(venue_name, [])  # Get availability data from all_slots
#             }

#         # Pass mapped venue data to the template
#         return render(request, 'request_booking/user_dashboard.html', {"venues": mapped_venues})

#     return HttpResponseNotAllowed(['GET'])

def user_dashboard(request):
    if request.method == "GET":
        print("Inside user_dashboard view")
        print("Request path:", request.path)
        print("Request headers:", request.headers)
        print('ooooooooooooooooooooo')

        # Retrieve stored venue slot availability from the session
        all_slots = request.session.get('all_slots', {})

        print(all_slots)

        # Extract venue names from all_slots
        venue_names = all_slots.keys()

        # Fetch venues from the database
        venues = Venue.objects.filter(venue_name__in=venue_names).values('venue_name', 'capacity', 'facilities', 'photo_url')

        # Map the venue data with availability
        formatted_venues = []

        for venue in venues:
            venue_name = venue['venue_name']
            formatted_venues.append({
                "name": venue_name,
                "capacity": venue['capacity'],
                "facilities": venue['facilities'],  # Assuming it's stored as a list in JSONField
                "images": venue['photo_url'].split(",") if venue['photo_url'] else [],  # Convert CSV string to list
            })

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

    




 


from django.http import JsonResponse
from django.db.models import Q, F
from datetime import datetime, timedelta
from .models import Venue





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













from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from .models import Venue, Request
import json

# @csrf_exempt  # Disable CSRF for testing purposes (not recommended in production)
# def book_venue(request):
#     if request.method == "POST":
#         venue_name = request.POST.get("venue_name")
#         print(f"Venue selected: {venue_name}")
#         return render(request, "request_booking/booking_form.html", {"venue": venue_name})

# @csrf_exempt
# def process_booking(request):
#     if request.method == "POST":
#         data = {
#             "event_type": request.POST.get("eventType"),
#             "other_event_type": request.POST.get("otherEventType"),
#             "first_name": request.POST.get("firstName"),
#             "last_name": request.POST.get("lastName"),
#             "email": request.POST.get("email"),
#             "phone": request.POST.get("phone"),
#             "venue": request.POST.get("venue"),
#             "guest_count": request.POST.get("guestCount"),
#             "purpose": request.POST.get("purpose"),
#         }
#         print(data)

#         # Save to database
#         venue_obj = Venue.objects.get(name=data["venue"]) if data["venue"] else None
#         Request.objects.create(
#             user=request.user,
#             date="2024-01-01",  # Default value (Replace with actual date input)
#             time=12,  # Default value (Replace with actual time input)
#             duration=2,  # Default duration (Replace with actual input)
#             venue=venue_obj,
#             need=data["purpose"],
#             event_details=data["event_type"],
#             status="pending",
#         )

#         return render(request, "request_booking/user_dashboard.html", {"success": True, "venue": data["venue"]})

#     return JsonResponse({"error": "Invalid request"}, status=400)



# from django.shortcuts import render, redirect
# from django.http import JsonResponse
# from django.views.decorators.csrf import csrf_exempt
# from .models import Venue, Request

# @csrf_exempt  # Not recommended in production; use Django’s CSRF protection
# def book_venue(request):
#     """Handles venue selection and preloads user session details."""
#     if request.method == "POST":
#         venue_name = request.POST.get("venue_name")
#         print(f"Venue selected: {venue_name}")

#         # Fetch user details from session
#         user_data = {
#             "first_name": request.session.get("first_name", ""),
#             "email": request.session.get("email", ""),
#             "organization_name": request.session.get("organization_name", ""),
#         }

#         return render(request, "request_booking/booking_form.html", {
#             "venue": venue_name,
#             "user_data": user_data  # Passing session data to prefill the form
#         })

# @csrf_exempt
# def process_booking(request):
#     """Processes the booking request and saves details in the database."""
#     if request.method == "POST":
#         data = {
#             "event_type": request.POST.get("eventType"),
#             "other_event_type": request.POST.get("otherEventType"),
#             "first_name": request.session.get("first_name"),  # From session
#             "email": request.session.get("email"),  # From session
#             "organization_name": request.session.get("organization_name"),  # From session
#             "phone": request.POST.get("phone"),
#             "venue": request.POST.get("venue"),
#             "guest_count": request.POST.get("guestCount"),
#             "purpose": request.POST.get("purpose"),
#         }
#         print(data)

#         # Save to database
#         venue_obj = Venue.objects.get(name=data["venue"]) if data["venue"] else None
#         Request.objects.create(
#             user=request.user,
#             date="2024-01-01",  # Default value (Replace with actual date input)
#             time=12,  # Default value (Replace with actual time input)
#             duration=2,  # Default duration (Replace with actual input)
#             venue=venue_obj,
#             need=data["purpose"],
#             event_details=data["event_type"],
#             status="pending",
#         )

#         return render(request, "request_booking/user_dashboard.html", {"success": True, "venue": data["venue"]})

#     return JsonResponse({"error": "Invalid request"}, status=400)

# def set_user_session(request):
#     """Sets user details in session before booking."""
#     if request.method == "POST":
#         request.session["first_name"] = request.POST.get("first_name")
#         request.session["email"] = request.POST.get("email")
#         request.session["organization_name"] = request.POST.get("organization_name")

#         return JsonResponse({"message": "User details saved in session"}, status=200)

#     return JsonResponse({"error": "Invalid request"}, status=400)


from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Venue, Request

# @csrf_exempt  # Not recommended in production; use Django’s CSRF protection
# def book_venue(request):
#     """Handles venue selection and preloads user session details."""
#     if request.method == "POST":
#         venue_name = request.POST.get("venue_name")
#         print(f"Venue selected: {venue_name}")

#         # Fetch user details from session
#         user_data = {
#             "name": request.session.get("name", ""),  # Full name from session
#             "email": request.session.get("email", ""),
#             "organization_name": request.session.get("organization_name", ""),
#         }

#         return render(request, "request_booking/booking_form.html", {
#             "venue": venue_name,
#             "user_data": user_data  # Passing session data to prefill the form
#         })


@csrf_exempt
def book_venue(request):
    """Handles venue selection and preloads user session details."""
    if request.method == "POST":
        venue_name = request.POST.get("venue_name")
        print(f"Venue selected: {venue_name}")

        # Print session data for debugging
        print("Session Data:", request.session.items())
        print(request.session.get("name"))

        # Fetch user details from session
        user_data = {
            # "name": request.session.get("name", "Name not found"),  # Full name from session
            # "email": request.session.get("email", "Email not found"),
            # "organization_name": request.session.get("organization_name", "Organization not found"),
            "name": request.session.get("name"),  # Full name from session
            "email": request.session.get("email"),
            "organization_name": request.session.get("organization_name"),
        }

        print('user data : ' , user_data)

        return render(request, "request_booking/booking_form.html", {
            "venue": venue_name,
            "user_data": user_data  # Passing session data to prefill the form
        })




@csrf_exempt
def process_booking(request):
    """Processes the booking request and saves details in the database."""
    if request.method == "POST":
        data = {
            "event_type": request.POST.get("eventType"),
            "other_event_type": request.POST.get("otherEventType"),
            "name": request.session.get("firstName"),  # Full name from session
            "email": request.session.get("email"),  # From session
            "organization_name": request.session.get("organization_name "),  # From session
            "phone": request.POST.get("phone"),
            "venue": request.POST.get("venue"),
            "guest_count": request.POST.get("guestCount"),
            "purpose": request.POST.get("additionalRequests"),
        }
        print(data)

        # Save to database
        venue_obj = Venue.objects.get(venue_name=data["venue"]) if data["venue"] else None
        Request.objects.create(
            user=request.user,
            date="2024-01-01",  # Default value (Replace with actual date input)
            time=12,  # Default value (Replace with actual time input)
            duration=2,  # Default duration (Replace with actual input)
            venue=venue_obj,
            need=data["purpose"],
            event_details=data["event_type"],
            status="pending",
        )

        return render(request, "request_booking/user_dashboard.html", {"success": True, "venue": data["venue"]})

    return JsonResponse({"error": "Invalid request"}, status=400)




from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Request

# @login_required
# def booking_status(request):
#     """
#     View to fetch and display all booking requests for the admin.
#     """
#     # Fetch all booking requests
#     requests = Request.objects.all().order_by('-date')  # Show latest bookings first

#     print('requests : ' , requests)

#     return render(request, "request_booking/booking_status.html", {"requests": requests})

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

    return render(request, "request_booking/booking_status.html", {"requests": requests , "person_name": person_name})

