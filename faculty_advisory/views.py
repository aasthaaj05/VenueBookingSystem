from django.shortcuts import render
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from services import booking_service
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


from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt

import sys
from django.http import HttpResponse

import traceback

from django.http import HttpResponse

from django.shortcuts import render

from django.shortcuts import render
from django.http import HttpResponseNotAllowed



from django.shortcuts import render
from django.http import HttpResponseNotAllowed

from django.shortcuts import render
from django.http import HttpResponseNotAllowed
from gymkhana.models import Venue  

from django.http import JsonResponse
from django.db.models import Q, F
from datetime import datetime, timedelta
from .models import Venue

from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from .models import Venue, Request
import json

# Create your views here.
@csrf_exempt
def get_pending_forward_requests(request):
    user_id=request.GET.get('user_id')
    if not user_id:
        return JsonResponse({'error': 'Missing user ID'}, status=400)
    try:
        result = booking_service.getForwardRequests(user_id)
        return JsonResponse(result, safe=False)
    except ValueError as e:
        return JsonResponse({'error': str(e)}, status=400)
    



@csrf_exempt
def accept_pending_forward_requests(request):
    if request.method != "POST":
        return JsonResponse({"error": "Only POST method allowed"}, status=405)

    data = json.loads(request.body)
    req_id=data.get('req_id')
    if not req_id:
        return JsonResponse({'error': 'Missing request ID'}, status=400)
    user_id=data.get('user_id')
    if not user_id:
        return JsonResponse({'error': 'Missing user ID'}, status=400)
    
    try:
        res = booking_service.forwardRequestToGymkhana(req_id, user_id)
        return JsonResponse({'success': res})
    except ValueError as e:
        return JsonResponse({'error': str(e)}, status=400)
    
def decline_pending_forward_requests(request):
    if request.method != "POST":
        return JsonResponse({"error": "Only POST method allowed"}, status=405)

    data = json.loads(request.body)
    req_id=data.get('req_id')
    if not req_id:
        return JsonResponse({'error': 'Missing request ID'}, status=400)
    user_id=data.get('user_id')
    if not user_id:
        return JsonResponse({'error': 'Missing user ID'}, status=400)
    
    try:
        res = booking_service.declineForwardRequest(req_id, user_id)
        return JsonResponse({'success': res})
    except ValueError as e:
        return JsonResponse({'error': str(e)}, status=400)
    
    


