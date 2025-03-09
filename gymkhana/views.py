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

from .models import Request, Booking, Venue, Rejection, RejectedBooking
from .serializers import (
    RequestSerializer,
    BookingSerializer,
    VenueSerializer,
    RejectionSerializer,
    RejectedBookingSerializer,
)

from users.models import CustomUser
from django.views.decorators.csrf import csrf_exempt



def home(request):
    return render(request , 'gymkhana/index.html')

@api_view(['POST'])
def create_venue(request):
    """
    Creates a new venue.
    Expects JSON payload with: venue_name, description, photo_url, capacity, address, facilities, department_incharge
    """
    serializer = VenueSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()  # Automatically generates UUID for id
        return Response({"message": "Venue created successfully", "venue": serializer.data}, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)





@api_view(['POST'])
# @permission_classes([IsAuthenticated])
@csrf_exempt
def approve_request(request, request_id):
    """Approve a request and create a booking."""
    req = get_object_or_404(Request, request_id=request_id)

    if req.status != 'pending':
        return Response({"error": "Request is not in a pending state."}, status=status.HTTP_400_BAD_REQUEST)

    req.status = 'approved'
    req.save()

    booking = Booking.objects.create(
        request=req,
        user=req.user,
        date=req.date,
        time=req.time,
        duration=req.duration,
        venue=req.venue,
        event_details=req.event_details,
        msg=req.msg
    )

    return Response({
        "message": "Request approved successfully.",
        "booking": BookingSerializer(booking).data
    }, status=status.HTTP_200_OK)


@api_view(['POST'])
# @permission_classes([IsAuthenticated])
def reject_request(request, request_id):
    """Reject a request and store the reason in the rejection table."""
    req = get_object_or_404(Request, request_id=request_id)

    if req.status != 'pending':
        return Response({"error": "Request is not in a pending state."}, status=status.HTTP_400_BAD_REQUEST)

    reason = request.data.get('reason', '')
    msg = request.data.get('msg', '')

    if not reason:
        return Response({"error": "Rejection reason is required."}, status=status.HTTP_400_BAD_REQUEST)

    req.status = 'rejected'
    req.reasons = reason
    req.save()

    rejection = Rejection.objects.create(
        request=req,
        user=req.user,
        reason=reason,
        msg=msg
    )

    return Response({
        "message": "Request rejected successfully.",
        "rejection": RejectionSerializer(rejection).data
    }, status=status.HTTP_200_OK)


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



@api_view(['POST'])  # Accept user_id in the request body
def requests_for_gymkhana(request):
    """
    Get all venue requests assigned to the gymkhana member based on `user_id`.
    """
    user_id = request.data.get("user_id")  # Get user_id from request body

    if not user_id:
        return Response({"error": "user_id is required"}, status=status.HTTP_400_BAD_REQUEST)

    # Ensure user_id is a valid UUID (if using UUIDs in CustomUser)
    try:
        gymkhana_user = get_object_or_404(CustomUser, id=user_id)
    except ValueError:
        return Response({"error": "Invalid user_id format"}, status=status.HTTP_400_BAD_REQUEST)

    # Find venues assigned to this Gymkhana department in-charge
    venues = Venue.objects.filter(department_incharge=gymkhana_user)

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


    # ✅ Filter requests where status is 'pending' OR 'waiting for approval'
    requests = Request.objects.select_related('venue', 'user').filter(
        Q(status="pending")
    )


    context = {
        'requests': [
            {
                'request_id': str(req.request_id),
                'date': req.date.strftime('%Y-%m-%d'),
                'time': f"{req.time}:00",  # Formatting time
                'venue': {
                    'name': req.venue.venue_name if hasattr(req.venue, 'venue_name') else 'Unknown Venue',
                    'capacity': req.venue.capacity if hasattr(req.venue, 'capacity') else 'N/A',
                },
                'user': {'organization_name': req.user.organization_name},
                'event_details': req.event_details,
                'status': req.status,
                'reasons': req.reasons if req.status == 'rejected' else None,
                'purpose' : req.need
            }
            for req in requests
        ]
    }
    print('context : ', context)  # Debugging output

    return render(request, 'gymkhana/view_request.html', context)




import uuid
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from .models import Request, Booking
from .serializers import BookingSerializer

def approve_request(request, request_id):
    if request.method == "POST":
        req = get_object_or_404(Request, request_id=request_id)

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

            return redirect('/gymkhana/request_booking')
        else:
            print("❌ Serializer errors:", serializer.errors)  # Debugging
            messages.error(request, "Error approving request.")

    return redirect('/gymkhana/request_booking')





def decline_request(request, request_id):
    if request.method == "POST":
        req = get_object_or_404(Request, request_id=request_id)
        reason = request.POST.get("rejection_reason", "No reason provided")  # Get rejection reason from form

        rejection_data = {
            "rejection_id": uuid.uuid4(),  # Generate new UUID
            "request": req.request_id,  # Link to original request
            "user": req.user.id,
            "date": req.date,
            "time": req.time,
            "duration": req.duration,
            "venue": req.venue.id,
            "event_details": req.event_details,
            "rejection_reason": reason
        }

        serializer = RejectedBookingSerializer(data=rejection_data)

        if serializer.is_valid():
            with transaction.atomic():
                serializer.save()  # Save rejected request
                
                # ✅ Update request status and add reason
                req.status = "rejected"
                req.reasons = reason  # Save reason in Request table
                req.save(update_fields=["status", "reasons"])

                print("❌ Request rejected and moved to RejectedBookings!")
                messages.success(request, "Request declined and logged.")

            return redirect('/gymkhana/request_booking')
        else:
            print("❌ Serializer errors:", serializer.errors)
            messages.error(request, "Error declining request.")

    return redirect('/gymkhana/request_booking')




from django.shortcuts import render, redirect
from django.http import JsonResponse
from .models import Venue
import uuid
import json

import uuid
import json
from datetime import datetime

def add_venue(request):
    if request.method == "GET":
        return render(request, "gymkhana/add_venue.html")  # Replace "template_name.html" with your actual template file.

    if request.method == "POST":

        print(f"Request Body: {request.body.decode('utf-8')}")
        print(f"Request POST Data: {request.POST}")

        venue_name = request.POST.get("venue_name")
        description = request.POST.get("description")
        photo_url = request.POST.get("photo_url")
        capacity = request.POST.get("capacity")
        address = request.POST.get("address")
        facilities = request.POST.get("facilities")
        department_incharge_id = request.POST.get("department_incharge")

        print('type of facilities : ',type(facilities))

        facilities=json.loads(facilities),  # Expecting JSON format


        # Debugging: Print values
        print('in add_venue func')
        print(f"Venue Name: {venue_name}")
        print(f"Description: {description}")
        print(f"Photo URL: {photo_url}")
        print(f"Capacity: {capacity}")
        print(f"Address: {address}")
        print(f"Facilities: {facilities}")
        print(f"Department Incharge ID: {department_incharge_id}")

        try:
            venue = Venue.objects.create(
                id=str(uuid.uuid4()),
                venue_name=venue_name,
                description=description,
                photo_url=photo_url,
                capacity=int(capacity),
                address=address,
                
                facilities = [item.strip() for item in facilities.split(",")] if facilities else [],
                department_incharge_id=department_incharge_id,
                created_at=datetime.now(),  # Manually setting current datetime
                updated_at=datetime.now()   # Manually setting current datetime
            )
            print('in try .. in add_venue func')
            return JsonResponse({"message": "Venue added successfully!"}, status=201)
        except Exception as e:
            print('in exception .. add_venue func')
            return JsonResponse({"error": str(e)}, status=400)

    return render(request, "add_venue.html")








def gymkhana_dashboard(request):
    return render(request, 'gymkhana/gymkhana_dashboard.html')  # Gymkhana dashboard template



