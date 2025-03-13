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
)

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



from django.contrib.auth import logout
from django.shortcuts import redirect

def logout_view(request):
    # Clear the session data
    request.session.flush()
    
    # Logout the user
    logout(request)
    
    # Redirect to login or homepage
    return redirect('/users/login')  # Change 'login' to the actual login page name



from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from request_booking.models import Request
from users.models import CustomUser  # Ensure the CustomUser model is properly imported


@csrf_exempt
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

@csrf_exempt
def get_requests(request):
    print("In Venue admin : get_requests()")
    print("Session:", request.session)

    user_id = str(request.session.get('user_id'))
    print('user_id : ', user_id)

    print("Request session items:", request.session.items())

    if not user_id:
        return JsonResponse({'error': 'Missing user ID'}, status=400)

    try:
        print('bbbbbbb')
        print()
        print()
        # Fetch logged-in venue admin details
        venue_admin = CustomUser.objects.get(id=user_id)
        print('venue admin : ' , venue_admin)
        print('venue admin.id : ' , venue_admin.id)
        venue_admin_id_str = str(venue_admin.id).replace('-', '')  # Convert to string before replacing
        print('venue admin.id : ' , venue_admin_id_str)


        # # Check if the logged-in user is a venue admin
        # if venue_admin.role != "venue_admin" or :
        #     return JsonResponse({'error': 'Access Denied'}, status=403)


        if venue_admin.role.lower() != "venue_admin":
            return JsonResponse({'error': 'Access Denied'}, status=403)



        print('aaaaaaaaaa')
        print()
        print()

        # Get venues where this venue admin is the department incharge
        managed_venues = Venue.objects.filter(department_incharge=venue_admin_id_str)

        print('ccccccccc')
        print()
        print()

        # Extract venue IDs
        managed_venue_ids = managed_venues.values_list('id', flat=True)


        print('ddddddd')
        print()
        print()

        # Get pending requests for these venues
        pending_requests = Request.objects.filter(venue_id__in=managed_venue_ids, status="pending")

        print("Managed Venues:", managed_venues)
        print("Pending Requests:", pending_requests)

        print()
        print()
        print('managed_venues : ' , managed_venues)
        print('pending_requests : ' , pending_requests)
        print()
        print()

        context = {
            'pending_requests': pending_requests,
            'user': request.user
        }


        return render(request, "venue_admin/venue_admin_get_pending_requests.html", context)

    except CustomUser.DoesNotExist:
        return JsonResponse({'error': 'User not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)
