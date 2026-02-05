from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponse, HttpResponseNotAllowed
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q, F, Count
from datetime import datetime, timedelta
import json
import sys
import traceback
import uuid  # ADDED: Missing import

from services import booking_service
from gymkhana.models import Booking, Venue

from request_booking.models import Request  # Replace 'your_app' with the actual app name where Request is defined


# ADDED: Helper function to convert decimal time to string format
def decimal_to_time_str(decimal_time):
    """
    Convert decimal time (e.g., 14.5) to time string (e.g., '2:30 PM')
    """
    try:
        hours = int(decimal_time)
        minutes = int((decimal_time - hours) * 60)
        
        # Convert to 12-hour format
        suffix = 'AM' if hours < 12 else 'PM'
        hour_12 = hours % 12
        if hour_12 == 0:
            hour_12 = 12
            
        return f"{hour_12}:{minutes:02d} {suffix}"
    except (ValueError, TypeError):
        return str(decimal_time)


def index(request):
    return render(request , 'faculty_advisor/index.html')


def faculty_advisor_dashboard(request):
    # return render(request, "faculty_advisor/faculty_advisor_dashboard.html")  
    return render(request, "faculty_advisor/index.html")  




from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from gymkhana.models import Venue  # Import models
from request_booking.models import Request
from users.models import CustomUser



from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

# @csrf_exempt
def get_pending_forward_requests(request):
    print("In get_pending_forward_requests()")
    print("Session:", request.session)

    user_id = request.session.get('user_id')

    print("Request session items:", request.session.items())

    if not user_id:
        return JsonResponse({'error': 'Missing user ID'}, status=400)

    try:
        # Fetch logged-in faculty advisor details
        faculty_ad = CustomUser.objects.get(id=user_id)

        # Check if the logged-in user is a faculty advisor
        if faculty_ad.role != "faculty_advisor":
            return JsonResponse({'error': 'Access Denied'}, status=403)

        # Fetch all pending requests
        pending_requests = Request.objects.filter(status='waiting_for_approval')


        # Filter requests where the requested user's organization matches the faculty advisor's organization
        filtered_requests = []
        for req in pending_requests:
            requested_user = CustomUser.objects.get(id=req.user_id)  # Get the user who made the request
            
            if requested_user.organization_name == faculty_ad.organization_name:
                filtered_requests.append(req)

        print("Filtered Requests:", filtered_requests)

        context = {
            'pending_requests': filtered_requests,
            'user': request.user
        }

        return render(request, "faculty_advisor/faculty_advisor_pending_requests.html", context)

    except CustomUser.DoesNotExist:
        return JsonResponse({'error': 'User not found'}, status=404)
    except Exception as e:
        print('---line 145 ----')
        return JsonResponse({'error': str(e)}, status=400)



    



# @csrf_exempt
def accept_pending_forward_requests(request, req_id):
    print('fac ad : in accept_pending_forward_requests() ')
    if request.method != "POST":
        return JsonResponse({"error": "Only POST method allowed"}, status=405)

    print("request id:", req_id)
    req_id = req_id.replace('-','')
    if not req_id:
        return JsonResponse({'error': 'Missing request ID'}, status=400)
    print("session:", request.session)
    user_id=request.session.get('user_id')
    user_id = user_id.replace('-','')

    if not user_id:
        print('in fac : if not user_id error ')
        return JsonResponse({'error': 'Missing user ID'}, status=400)
    
    try:
        req_id = req_id.replace('-','')
        res = booking_service.forwardRequestToGymkhana(req_id, user_id)
        
        return redirect('/faculty_advisor/forward_requests/')
        #return JsonResponse({'success': res})
    except ValueError as e:
        return JsonResponse({'error': str(e)}, status=400)




def decline_pending_forward_requests(request, req_id):
    if request.method != "POST":
        return JsonResponse({"error": "Only POST method allowed"}, status=405)
    if not req_id:
        return JsonResponse({'error': 'Missing request ID'}, status=400)
    print("session:", request.session)
    user_id=request.session.get('user_id')
    if not user_id:
        return JsonResponse({'error': 'Missing user ID'}, status=400)
    
    try:
        res = booking_service.declineForwardRequest(req_id, user_id)

        return redirect('/faculty_advisor/forward_requests')
        #return JsonResponse({'success': res})
    except ValueError as e:
        return JsonResponse({'error': str(e)}, status=400)
    

    






from django.http import JsonResponse
from django.views import View
from django.core.serializers import serialize
from django.utils import timezone
from datetime import datetime, timedelta
import json





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
        return render(request, 'faculty_advisor/venue_schedule.html', {'venue_data': venue_data})


class BookingScheduleAPI(View):

    def get(self, request):
        print('inside BookingScheduleAPI GET')
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
            

            
            # FIXED: Get bookings for the venue and date range
            # Changed to filter only active/approved bookings
            bookings = Booking.objects.filter(
                venue_id=venue_uuid,
                date__gte=start_date_obj,
                date__lte=end_date_obj,
                status='active'  # ADDED: Only show active (approved) bookings in schedule
            ).select_related('user', 'venue')

            print('bookings->',bookings)
            print(f'Found {bookings.count()} active bookings')
            
            # Prepare response data
            bookings_data = []
            for booking in bookings:
                # Convert duration to float if it's stored as string
                try:
                    duration_float = float(booking.duration)
                except (ValueError, TypeError):
                    duration_float = 1.0  # Default 1 hour if conversion fails
                
                bookings_data.append({
                    'id': str(booking.booking_id),
                    'date': booking.date.isoformat(),
                    'time': decimal_to_time_str(booking.time),  # Using the conversion function
                    'duration': duration_float,
                    'event_details': booking.event_details,
                    'user_name': f"{booking.user.name}",
                    'status': booking.status,  # FIXED: Use actual status field instead of get_status_display()
                    'venue_name': booking.venue.venue_name,
                    'email': booking.user.email,
                })
            print('bookings_data->',bookings_data)


            # FIXED: Booking statistics - now properly counts by status
            # Get all bookings (not just confirmed) for statistics
            all_bookings = Booking.objects.filter(
                venue_id=venue_uuid,
                date__gte=start_date_obj,
                date__lte=end_date_obj
            )
            
            status_counts = all_bookings.values('status').annotate(count=Count('booking_id'))
            print("\n\n\n")
            print('status_counts->',status_counts)
            print("\n\n\n")
            
            stats = {
                'total_bookings': all_bookings.count(),
                'active': 0,
                'pending': 0,
                'cancelled': 0,
                'user_cancelled': 0,
            }

            for entry in status_counts:
                status = entry['status']
                count = entry['count']
                if status == 'active':  # FIXED: Using 'active' instead of 'confirmed'
                    stats['active'] = count
                elif status == 'pending':
                    stats['pending'] = count
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