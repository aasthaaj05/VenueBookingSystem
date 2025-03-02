from django.shortcuts import render

# Create your views here.

from django.contrib.auth import authenticate, login
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import CustomUser
from .serializers import RegisterSerializer, LoginSerializer, UserSerializer


from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages














from django.contrib.auth import authenticate, login
from rest_framework.decorators import api_view, renderer_classes
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework import status
from .serializers import LoginSerializer

from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .serializers import LoginSerializer



from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from django.http import JsonResponse

CustomUser = get_user_model()

def store_user_session(request, email):
    user = get_object_or_404(CustomUser, email=email)  # Fetch user by email
    
    # Storing user details in session
    request.session['user_id'] = str(user.id)  # Store UUID as string
    request.session['name'] = user.name
    request.session['email'] = user.email
    request.session['organization_name'] = user.organization_name
    request.session['organization_type'] = user.organization_type
    request.session['role'] = user.role
    request.session['is_active'] = user.is_active
    request.session['created_at'] = user.created_at.strftime('%Y-%m-%d %H:%M:%S')

    return JsonResponse({"message": "User details stored in session successfully"})







from django.http import JsonResponse

def print_all_session_data(request):
    """Function to print all session data in the console."""
    print("\n--- SESSION DATA ---")
    
    if not request.session.keys():
        print("No session data found")
    else:
        for key in request.session.keys():
            print(f"{key}: {request.session.get(key)}")
    
    print("--------------------\n")




@api_view(['GET', 'POST'])  # Accept both GET and POST
def login_view(request):
    print('pppppppppppppppppppppppppppppppppppppppp')
    # Handle GET request (render the login page)
    if request.method == 'GET':
        return render(request, 'users/login.html')  # Replace with your actual template path
    
    # Handle POST request (form submission or API call)
    if request.content_type == 'application/json':
        print('handle post -- login')
        # Handle API request with JSON data
        serializer = LoginSerializer(data=request.data)
        
        if serializer.is_valid():
            email = serializer.validated_data['email']
            password = serializer.validated_data['password']
            
            user = authenticate(request, username=email, password=password)
            if user is None:
                return Response({"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)
            
            login(request, user)


            # Store user details in session
            request.session['name'] = user.get_full_name()
            request.session['email'] = user.email
            request.session['organization_name'] = user.profile.organization_name  # Assuming user has a profile with organization_name

            print('login_view function : ')
            print('name : ' , request.session.get('name'))
            print('email : ' , request.session.get('email'))
            print('organization_name : ' , request.session.get('organization_name'))
            print('----------')

            return Response({"message": "Login successful", "user_id": str(user.id)}, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    else:
        print('iufoijfoisfoijdjijgodjidoj')
        # Handle traditional form submission
        username = request.POST.get('username')
        password = request.POST.get('password')

        print('in login_view else part')
        print('username : ', username)
        print('password : ' , password)

        request.session['email'] = username

        store_user_session(request , username)


        print_all_session_data(request)
        

        
        user = authenticate(request, username=username, password=password)
        if user is None:
            # Redirect back to login page with error
            return render(request, 'users/login.html', {'error': 'Invalid credentials'})
        
        login(request, user)
        print('dkcfooiduvodgodugod')
        # Redirect to dashboard or home page after successful login
        return redirect('/users/home')  # Replace with your actual success redirect URL name












from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import login
from django.contrib import messages
import re







from django.shortcuts import render, redirect
from django.contrib.auth import login
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .serializers import RegisterSerializer

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

            # ✅ Storing user details in session
            request.session['user_id'] = str(user.id)  # Store UUID as string
            request.session['name'] = user.name
            request.session['email'] = user.email
            request.session['organization_name'] = user.organization_name
            request.session['organization_type'] = user.organization_type
            request.session['role'] = user.role
            request.session['is_active'] = user.is_active
            request.session['created_at'] = user.created_at.strftime('%Y-%m-%d %H:%M:%S')
            
            # Redirect to dashboard or login page after successful registration
            return redirect('/users/home')  # Change 'dashboard' to your actual view name

        # If validation fails, re-render the form with errors
        print('oziufoisuffsffpf')
        return render(request, 'users/register.html', {'errors': serializer.errors})


    
    






@api_view(['GET'])
def get_users(request):
    users = CustomUser.objects.all()
    serializer = UserSerializer(users, many=True)
    return Response(serializer.data)




from django.shortcuts import render

def home(request):
    return render(request, 'users/home.html')




from django.shortcuts import render

# def calendar_view(request):
#     if request.method == 'GET':
#         return render(request, 'users/calendar.html')
#     return render(request, 'users/calendar.html')

from django.http import HttpResponse

def calendar_view(request):
    if request.method == "GET":
        return render(request, 'users/calendar.html')
    
    # If it's a POST request, check if there's a redirect happening here
    if request.method == "POST":
        print("Inside calendar_view POST request")
        return HttpResponse("Calendar POST request received")  # Debugging



from django.shortcuts import render
from django.http import JsonResponse
import json

def index(request):
    return render(request, 'users/calendar.html')



from django.views.decorators.csrf import csrf_exempt




@csrf_exempt  # Disable CSRF protection for this view
def submit_booking(request):
    print('fojdofudogjoejg')
    if request.method == 'POST':
        try:
            print('iiiii')
            data = json.loads(request.body)  # Receive JSON data from frontend
            print('data : ', data)
            selected_date = data.get('date')
            selected_time = data.get('time')

            print(data)

            print('fjjfof')

            if not selected_date or not selected_time:
                return JsonResponse({'message': 'Invalid input'}, status=400)

            print(f"Booking received - Date: {selected_date}, Time: {selected_time}")

            

            return JsonResponse({
                'message': 'Booking confirmed',
                'date': selected_date,
                'time': selected_time
            })
        except json.JSONDecodeError:
            return JsonResponse({'message': 'Invalid JSON format'}, status=400)
    
    return JsonResponse({'message': 'Invalid request method'}, status=405)



