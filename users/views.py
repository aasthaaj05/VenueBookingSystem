
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





CustomUser = get_user_model()

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




# @api_view(['GET', 'POST'])  # Accept both GET and POST
# def login_view(request):
#     # Flush existing session
#     request.session.flush()
    
#     print('in login_view function\n\n')
#     # Handle GET request (render the login page)
#     if request.method == 'GET':
#         return render(request, 'users/login.html')  # Replace with your actual template path
    
#     # # Handle POST request (form submission or API call)
#     # if request.content_type == 'application/json':
#     #     print('handle post -- login')
#     #     # Handle API request with JSON data
#     #     serializer = LoginSerializer(data=request.data)
        
#     #     if serializer.is_valid():
#     #         email = serializer.validated_data['email']
#     #         password = serializer.validated_data['password']
            
#     #         user = authenticate(request, username=email, password=password)
#     #         if user is None:
#     #             # return Response({"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)
#     #             return render(request, 'users/login.html')
            
#     #         login(request, user)


#     #         # Store user details in session
#     #         request.session['name'] = user.get_full_name()
#     #         request.session['email'] = user.email
#     #         request.session['organization_name'] = user.profile.organization_name  # Assuming user has a profile with organization_name

#     #         print('login_view function : ')
#     #         print('name : ' , request.session.get('name'))
#     #         print('email : ' , request.session.get('email'))
#     #         print('organization_name : ' , request.session.get('organization_name'))
#     #         print('----------')

#     #         return Response({"message": "Login successful", "user_id": str(user.id)}, status=status.HTTP_200_OK)
        
#     #     # return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#     #     return render(request, 'users/login.html')
    
#     # else:
#     print('in else part of login_view function')
#         # Handle traditional form submission
#     username = request.POST.get('username')
#     password = request.POST.get('password')

#     print('in login_view else part')
#     print('username : ', username)
#     print('password : ' , password)

#     request.session['email'] = username
        
#     print_all_session_data(request)
        
#     user = authenticate(request, username=username, password=password)
#     if user is None:
#             # Redirect back to login page with error
#             # return render(request, 'users/login.html', {'error': 'Invalid credentials'})
#         return render(request, 'users/login.html')
        
#     login(request, user)
#     print('user logged in! .. login_view func')

#     print('login_view part1')
#     store_user_session(request , username)
#     print('login_view part2')
        
#     print('request.user.role : ' , request.user.role)


#         # # Assuming user role is stored in request.user.role
#         # if request.user.role in ["Gymkhana",'gymkhana']:
#         #     return redirect('/gymkhana/dashboard')  # Redirect Gymkhana users to a different page
#         # elif request.user.role in ["faculty_advisor",'Faculty_advisor']:
#         #     return redirect('/faculty_advisor/home')  # Redirect Gymkhana users to a different page
#         # elif request.user.role in ["venue_admin",'Venue_admin']:
#         #     return redirect('/venue_admin/home')  
#         # else:
#         #     return redirect('/request_booking/home')


#     if request.user.role in ["faculty_advisor",'Faculty_advisor']:
#         return redirect('/faculty_advisor/home')  
#     elif request.user.role in ["venue_admin",'Venue_admin']:
#         return redirect('/venue_admin/home')  
#     else:
#         return redirect('/request_booking/home')






# @api_view(['GET', 'POST'])  # Accept both GET and POST
# def login_view(request):
#     print()
#     print()

#     # Flush existing session
#     request.session.flush()
    
#     print('in login_view function\n\n')

#     if request.method == 'GET':
#         return render(request, 'users/login.html')  
    

#     username = request.POST.get('username')
#     password = request.POST.get('password')

#     print('in login_view else part')
#     print('username : ', username)
#     print('password : ' , password)

    
        
#     user = authenticate(request, username=username, password=password)

#     if user is None:
#         return render(request, 'users/login.html')

#     # request.session['email'] = username
#     request.session['email'] = user.email

        
#     print_all_session_data(request)
        
#     login(request, user)
#     print('user logged in! .. login_view func')

    

#     print('login_view part1')
#     store_user_session(request , username)
#     print('login_view part2')
        
#     print('request.user.role : ' , request.user.role)
#     print()
#     print()
#     print()
#     print()

#     if request.user.role in ["faculty_advisor",'Faculty_advisor']:
#         return redirect('/faculty_advisor/home')  
#     elif request.user.role in ["venue_admin",'Venue_admin']:
#         return redirect('/venue_admin/home')  
#     elif request.user.role in ["faculty",'Faculty']:
#         return redirect('/faculty_advisor/home')  
#     else:
#         return redirect('/users/login')


@api_view(['GET', 'POST'])
def login_view(request):
    # Flush existing session only on GET requests
    if request.method == 'GET':
        request.session.flush()
        return render(request, 'users/login.html')
    
    # Handle POST request
    username = request.POST.get('username')
    password = request.POST.get('password')
    
    # Don't print credentials in production code
    # print('username : ', username)  # Remove this
    # print('password : ', password)  # Remove this
    
    user = authenticate(request, username=username, password=password)
    if user is None:
        return render(request, 'users/login.html')
    
    # Set session data and login
    request.session['email'] = user.email
    login(request, user)
    
    # Store additional session data if needed
    store_user_session(request, username)
    
    # Handle redirects based on role
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



# @csrf_exempt  # Disable CSRF protection for this view
# def submit_booking(request):
#     print('in submit_booking function')
#     if request.method == 'POST':
#         try:
#             print('in try method .. submit_booking func')
#             data = json.loads(request.body)  # Receive JSON data from frontend
#             print('data : ', data)
#             selected_date = data.get('date')
#             selected_time = data.get('time')

#             print(data) 

#             if not selected_date or not selected_time:
#                 return JsonResponse({'message': 'Invalid input'}, status=400)

#             print(f"Booking received - Date: {selected_date}, Time: {selected_time}")
            

#             return JsonResponse({
#                 'message': 'Booking confirmed',
#                 'date': selected_date,
#                 'time': selected_time
#             })
#         except json.JSONDecodeError:
#             return JsonResponse({'message': 'Invalid JSON format'}, status=400)
    
#     return JsonResponse({'message': 'Invalid request method'}, status=405)



from django.contrib import messages
from django.shortcuts import redirect

def clear_flash_and_redirect(request):
    # Access all messages to ensure they are consumed (thus cleared)
    list(messages.get_messages(request))  # This clears flash messages
    return redirect('auth_otp:forgot_password')





