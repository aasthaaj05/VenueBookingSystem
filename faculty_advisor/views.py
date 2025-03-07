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


def faculty_advisor_dashboard(request):
    return render(request, "faculty_advisor/faculty_advisor_dashboard.html")  

# Create your views here.
@csrf_exempt
def get_pending_forward_requests(request):
    print("herhwjkfhw")
    print("session:", request.session)
    user_id=request.session.get('user_id')
    if not user_id:
        return JsonResponse({'error': 'Missing user ID'}, status=400)
    try:
        result = booking_service.getForwardRequests(user_id)
        context={
            'pending_requests':result,
            'user':request.user
        }
        print(result)
        return render(request, "faculty_advisor/faculty_advisor_pending_requests.html", context)
    except ValueError as e:
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
        return JsonResponse({'success': res})
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
        return JsonResponse({'success': res})
    except ValueError as e:
        return JsonResponse({'error': str(e)}, status=400)
    
    


