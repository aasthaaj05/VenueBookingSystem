from django.db.models import Count

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, get_user_model
from django.contrib import messages
from django.contrib.auth.models import User
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
import json
import re

from rest_framework.decorators import api_view, renderer_classes
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework import status

from .models import CustomUser
from .serializers import RegisterSerializer, LoginSerializer, UserSerializer
from gymkhana.models import Venue
from gymkhana.models import Booking
import uuid



CustomUser = get_user_model()


from django.http import JsonResponse
from django.views import View
from django.core.serializers import serialize
from django.utils import timezone
from datetime import datetime, timedelta
import json



def decimal_to_time_str(decimal_time):
    """
    Convert decimal time to HH:MM AM/PM format
    
    Args:
        decimal_time (float/str): Time in decimal format (e.g., 7.5 for 7:30 AM)
        
    Returns:
        str: Time in HH:MM AM/PM format (e.g., "7:30 AM")
        
    Examples:
        >>> decimal_to_time_str(7.5)
        '7:30 AM'
        >>> decimal_to_time_str(13.75)
        '1:45 PM'
        >>> decimal_to_time_str('14.25')
        '2:15 PM'
    """
    try:
        # Convert to float if it's a string
        decimal_time = float(decimal_time)
        
        # Extract hours and minutes
        hours = int(decimal_time)
        minutes = int(round((decimal_time - hours) * 60))
        
        # Handle overflow (e.g., 7.999 should become 8:00, not 7:59)
        if minutes >= 60:
            hours += 1
            minutes -= 60
        
        # Determine AM/PM and convert to 12-hour format
        period = 'AM' if hours < 12 else 'PM'
        display_hours = hours if hours <= 12 else hours - 12
        
        # Handle special case for 0 hours (midnight)
        if display_hours == 0:
            display_hours = 12
            period = 'AM'
            
        return f"{display_hours}:{minutes:02d} {period}"
    except (ValueError, TypeError):
        # Return a default value or raise an exception if you prefer
        return "12:00 AM"



def store_user_session(request, email):
    print('in store user session function part 1')
    user = get_object_or_404(CustomUser, email=email)  # Fetch user by email

    print('in store user session function part 2')
    
    # Storing user details in session
    request.session['user_id'] = str(user.id).replace('-','')  # Store UUID as string
    request.session['name'] = user.name
    request.session['email'] = user.email
    request.session['organization_name'] = user.organization_name
    request.session['organization_type'] = user.organization_type
    request.session['role'] = user.role
    request.session['is_active'] = user.is_active
    request.session['created_at'] = user.created_at.strftime('%Y-%m-%d %H:%M:%S')

    print('in store user session function part 3')

    return JsonResponse({"message": "User details stored in session successfully"})



def print_all_session_data(request):
    """Function to print all session data in the console."""
    print("\n--- SESSION DATA ---")
    
    if not request.session.keys():
        print("No session data found")
    else:
        for key in request.session.keys():
            print(f"{key}: {request.session.get(key)}")
    
    print("--------------------\n")


from django.contrib.messages import get_messages
from django.contrib import messages

@api_view(['GET', 'POST'])
def login_view(request):

    if request.method == 'GET':

        # Clear old messages
        storage = get_messages(request)
        for _ in storage:
            pass

        request.session.flush()
        return render(request, 'users/login.html')

    username = request.POST.get('username')
    password = request.POST.get('password')

    user = authenticate(request, username=username, password=password)

    if user is None:
        messages.error(request, "Invalid email or password", extra_tags="login")
        return render(request, 'users/login.html')

    request.session['email'] = user.email
    login(request, user)

    store_user_session(request, username)

    if request.user.role.lower() in ["faculty_advisor", "faculty"]:
        return redirect('/faculty_advisor/home')
    elif request.user.role.lower() in ["venue_admin"]:
        return redirect('/venue_admin/home')
    else:
        return redirect('/users/login')


@api_view(['GET', 'POST'])
def register_view(request):
    print('in register_view function')
    if request.method == 'GET':
        return render(request, 'users/register.html')

    elif request.method == 'POST':
        print(request.POST)  # Debugging: Check what data is coming in

        
        serializer = RegisterSerializer(data=request.POST)  # Use request.POST for form data
        
        if serializer.is_valid():
            user = serializer.save()
            login(request, user)
            print('User auto logged from register_view in successfully')

            # Storing user details in session
            request.session['user_id'] = str(user.id)  # Store UUID as string
            request.session['name'] = user.name
            request.session['email'] = user.email
            request.session['organization_name'] = user.organization_name
            request.session['organization_type'] = user.organization_type
            request.session['role'] = user.role
            request.session['is_active'] = user.is_active
            request.session['created_at'] = user.created_at.strftime('%Y-%m-%d %H:%M:%S')
            
            

            print('request.user.role : ' , user.role)
            if user.role in ["Gymkhana",'gymkhana']:
                return redirect('/gymkhana/dashboard')  
            elif user.role in ["faculty_advisor",'Faculty_advisor']:
                return redirect('/faculty_advisor/faculty_advisor_dashboard')  
            elif request.user.role in ["venue_admin",'Venue_admin']:
                return redirect('/venue_admin/home')  
            else:
                return redirect('/users/home')  # Default redirection for other users

        # If validation fails, re-render the form with errors
        return render(request, 'users/register.html', {'errors': serializer.errors})





@api_view(['GET'])
def get_users(request):
    users = CustomUser.objects.all()
    serializer = UserSerializer(users, many=True)
    return Response(serializer.data)



def home(request):
    return render(request, 'users/home.html')

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


def calendar_view(request):
    print('222222222')
    if request.method == "GET":
        return render(request, 'users/calendar.html')
    
    # If it's a POST request, check if there's a redirect happening here
    if request.method == "POST":
        print()
        print()
        print('in caledar_view function')
        # session = request.get('venue.name')
        print('request : ', request)
        print_request_details(request)
        venue_id = request.POST.get("venue_id")  # Get the venue name from the form

        venue_id_no_hyphen = venue_id.replace("-", "")
        print('venue-id (no hyphen) : ',venue_id_no_hyphen)
        request.session["venue_id"] = venue_id 
        print("Venue id:", venue_id)


        venue = get_object_or_404(Venue, id=venue_id)
        print('venue-name : ',venue.venue_name)  # Output the venue name
        print()
        print()

        request.session["venue_name"] = venue.venue_name

        print("Venue name stored in session:", request.session.get("venue_name"))  # Debugging print

        return render(request, 'users/calendar.html')
        print("Inside calendar_view POST request")
        return HttpResponse("Calendar POST request received")  # Debugging


def index(request):
    return render(request, 'users/calendar.html')





from django.contrib import messages
from django.shortcuts import redirect

def clear_flash_and_redirect(request):
    # Access all messages to ensure they are consumed (thus cleared)
    list(messages.get_messages(request))  # This clears flash messages
    return redirect('auth_otp:forgot_password')






from django.http import JsonResponse
from django.views import View
from django.core.serializers import serialize
from django.utils import timezone
from datetime import datetime, timedelta
import json






from django.forms.models import model_to_dict



class VenueListView(View):
    def get(self, request):
        venues = Venue.objects.all()
        print('venues->', venues)
        
        # Manually create the dictionary instead of using model_to_dict
        venue_data = [{
            'id': str(venue.id),  # Convert UUID to string
            'venue_name': venue.venue_name
        } for venue in venues]
        
        print('venue_data->', venue_data)
        return render(request, 'users/venue_schedule.html', {'venue_data': venue_data})


class BookingScheduleAPI(View):

    def get(self, request):
        print('Users : inside BookingScheduleAPI GET')
        print('Users : inside BookingScheduleAPI GET')
        print('Users : inside BookingScheduleAPI GET')
        print('Users : inside BookingScheduleAPI GET')
        print('Users : inside BookingScheduleAPI GET')


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


            # Fetch the venue and its capacity
            try:
                venue = Venue.objects.get(id=venue_uuid)
                venue_capacity = venue.capacity
                print('venue_capacity->',venue_capacity)
            except Venue.DoesNotExist:
                return JsonResponse({'error': 'Venue not found'}, status=404)
            

            
            # Get bookings for the venue and date range
            bookings = Booking.objects.filter(
                venue_id=venue_uuid,
                date__gte=start_date_obj,
                date__lte=end_date_obj,
                status='active',
            ).select_related('user', 'venue')

            print('bookings->',bookings)
            
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
                    'phone_number' : booking.request.phone_number,
                })
            print('bookings_data->',bookings_data)


            # Booking statistics
            status_counts = bookings.values('status').annotate(count=Count('venue_id'))
            print("\n\n\n")
            print('bookings.exists()->',bookings.exists())  # Should return True if there are records
            print("\n\n\n")
            print('status_counts->',status_counts)
            print("\n\n\n")
            stats = {
                'total_bookings': bookings.count(),
                'active': 0,
                'cancelled': 0,
                'user_cancelled': 0,
                'venue_capacity':venue_capacity,
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

