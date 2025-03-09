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

# Create your views here.
# @csrf_exempt
# def get_pending_forward_requests(request):
#     print("In get_pending_forward_requests()")
#     print("session:", request.session)

#     user_id=request.session.get('user_id')

#     if not user_id:
#         return JsonResponse({'error': 'Missing user ID'}, status=400)
#     try:
#         # result = booking_service.getForwardRequests(user_id)
#         # print('result', result)
#         # context={
#         #     'pending_requests':result,
#         #     'user':request.user
#         # }
#         # Fetch requests where the user_id matches and status is 'pending'
#         pending_requests = Request.objects.filter(user_id=user_id, status='pending')

#         print("Pending Requests:", pending_requests)

#         context = {
#             'pending_requests': pending_requests,
#             'user': request.user
#         }
        
#         print(pending_requests)
#         return render(request, "faculty_advisor/faculty_advisor_pending_requests.html", context)
#     except ValueError as e:
#         return JsonResponse({'error': str(e)}, status=400)


from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from gymkhana.models import Venue  # Import models
from request_booking.models import Request

@csrf_exempt
def get_pending_forward_requests(request):
    print("In get_pending_forward_requests()")
    print("session:", request.session)

    user_id = request.session.get('user_id')

    if not user_id:
        return JsonResponse({'error': 'Missing user ID'}, status=400)

    try:
        # Step 1: Get venues where the user is the in-charge
        venues_incharge = Venue.objects.filter(department_incharge=user_id).values_list('id', flat=True)

        # Step 2: Fetch requests for those venues where status is 'pending'
        pending_requests = Request.objects.filter(venue_id__in=venues_incharge, status='pending')

        print("Pending Requests:", pending_requests)

        context = {
            'pending_requests': pending_requests,
            'user': request.user
        }

        return render(request, "faculty_advisor/faculty_advisor_pending_requests.html", context)

    except Exception as e:
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
    
    


