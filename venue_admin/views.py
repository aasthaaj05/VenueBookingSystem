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



# from django.shortcuts import render
# from django.http import JsonResponse
# from django.views.decorators.csrf import csrf_exempt
# from request_booking.models import Request
# from users.models import CustomUser  # Ensure the CustomUser model is properly imported


# @csrf_exempt
# def get_pending_forward_requests(request):
#     print("In get_pending_forward_requests()")
#     print("Session:", request.session)

#     user_id = request.session.get('user_id')

#     print("Request session items:", request.session.items())

#     if not user_id:
#         return JsonResponse({'error': 'Missing user ID'}, status=400)

#     try:
#         # Fetch logged-in faculty advisor details
#         faculty_ad = CustomUser.objects.get(id=user_id)

#         # Check if the logged-in user is a faculty advisor
#         if faculty_ad.role != "faculty_advisor":
#             return JsonResponse({'error': 'Access Denied'}, status=403)

#         # Fetch all pending requests
#         pending_requests = Request.objects.filter(status='waiting_for_approval')


#         # Filter requests where the requested user's organization matches the faculty advisor's organization
#         filtered_requests = []
#         for req in pending_requests:
#             requested_user = CustomUser.objects.get(id=req.user_id)  # Get the user who made the request
            
#             if requested_user.organization_name == faculty_ad.organization_name:
#                 filtered_requests.append(req)

#         print("Filtered Requests:", filtered_requests)

#         context = {
#             'pending_requests': filtered_requests,
#             'user': request.user
#         }

#         return render(request, "faculty_advisor/faculty_advisor_pending_requests.html", context)

#     except CustomUser.DoesNotExist:
#         return JsonResponse({'error': 'User not found'}, status=404)
#     except Exception as e:
#         print('---line 145 ----')
#         return JsonResponse({'error': str(e)}, status=400)

# @csrf_exempt
# def get_requests(request):
#     print("In Venue admin : get_requests()")
#     print("Session:", request.session)
    
#     user_id = str(request.session.get('user_id'))
#     print('user_id : ', user_id)

#     print("Request session items:", request.session.items())

#     if not user_id:
#         return JsonResponse({'error': 'Missing user ID'}, status=400)

#     try:
#         print('bbbbbbb')
#         print()
#         print()
#         # Fetch logged-in venue admin details
#         venue_admin = CustomUser.objects.get(id=user_id)
#         print('venue admin : ' , venue_admin)
#         print('venue admin.id : ' , venue_admin.id)
#         venue_admin_id_str = str(venue_admin.id).replace('-', '')  # Convert to string before replacing
#         print('venue admin.id : ' , venue_admin_id_str)


#         # # Check if the logged-in user is a venue admin
#         # if venue_admin.role != "venue_admin" or :
#         #     return JsonResponse({'error': 'Access Denied'}, status=403)


#         if venue_admin.role.lower() != "venue_admin":
#             return JsonResponse({'error': 'Access Denied'}, status=403)



#         print('aaaaaaaaaa')
#         print()
#         print()

#         # Get venues where this venue admin is the department incharge
#         managed_venues = Venue.objects.filter(department_incharge=venue_admin_id_str)

#         print('ccccccccc')
#         print()
#         print()

#         # Extract venue IDs
#         managed_venue_ids = managed_venues.values_list('id', flat=True)


#         print('ddddddd')
#         print()
#         print()

#         # Get pending requests for these venues
#         pending_requests = Request.objects.filter(venue_id__in=managed_venue_ids, status="pending")

#         print("Managed Venues:", managed_venues)
#         print("Pending Requests:", pending_requests)

#         print()
#         print()
#         print('managed_venues : ' , managed_venues)
#         print('pending_requests : ' , pending_requests)
#         print()
#         print()

#         context = {
#             'pending_requests': pending_requests,
#             'user': request.user
#         }


#         return render(request, "venue_admin/venue_admin_get_pending_requests.html", context)

#     except CustomUser.DoesNotExist:
#         return JsonResponse({'error': 'User not found'}, status=404)
#     except Exception as e:
#         return JsonResponse({'error': str(e)}, status=400)


# def reject_request(request, request_id):
#     print("""Reject a request and store the reason in the rejection table.""")
#     req = get_object_or_404(Request, request_id=request_id)

#     print("""23r23fr23frq23r Reject a request and store the reason in the rejection table.""")

#     if req.status != 'pending':
#         return Response({"error": "Request is not in a pending state."}, status=status.HTTP_400_BAD_REQUEST)

#     # reason = request.data.get('reason', '')
#     # msg = request.data.get('msg', '')

#     # if not reason:
#     #     return Response({"error": "Rejection reason is required."}, status=status.HTTP_400_BAD_REQUEST)

#     print("#############################################Req found!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")

#     req.status = 'rejected'
#     req.reasons = ''
#     req.save()

#     rejection = Rejection.objects.create(
#         request=req,
#         user=req.user,
#         msg='Slot already booked'
#     )

#     return Response({
#         "message": "Request rejected successfully.",
#         "rejection": RejectionSerializer(rejection).data
#     }, status=status.HTTP_200_OK)

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

    data = {
        "message": "Request rejected successfully.",
        "rejection": RejectionSerializer(rejection).data
    }

    return JsonResponse(data, status=200)



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




import uuid
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from gymkhana.models import Request, Booking
from gymkhana.serializers import BookingSerializer

def forward_request_to_alternate(request):
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
        

def approve_request(request, request_id):

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