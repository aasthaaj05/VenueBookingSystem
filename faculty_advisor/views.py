from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponse, HttpResponseNotAllowed
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q, F
from datetime import datetime, timedelta
import json
import sys
import traceback

from services import booking_service
from gymkhana.models import Booking, Venue

from request_booking.models import Request  # Replace 'your_app' with the actual app name where Request is defined



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
def accept_pending_forward_requests(request, req_id):
    if request.method != "POST":
        return JsonResponse({"error": "Only POST method allowed"}, status=405)

    print("request id:", req_id)
    if not req_id:
        return JsonResponse({'error': 'Missing request ID'}, status=400)
    print("session:", request.session)
    user_id=request.session.get('user_id')
    if not user_id:
        return JsonResponse({'error': 'Missing user ID'}, status=400)
    
    try:
        req_id = req_id.replace('-','')
        res = booking_service.forwardRequestToGymkhana(req_id, user_id)
        
        return redirect('/faculty_advisor/forward_requests')
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
    
    


