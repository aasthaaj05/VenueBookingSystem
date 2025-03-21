from django.shortcuts import render, redirect
from django.contrib import messages
from .utils import send_otp  # Import the send_otp function





from django.shortcuts import render, redirect
from django.contrib import messages
from users.models import CustomUser  # Import the CustomUser model

def change_password_view(request):
    if request.method == 'POST':
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')
        email = request.session.get('email')  # Get email from session (set during OTP verification)

        if email:
            try:
                user = CustomUser.objects.get(email=email)  # Fetch user by email
                if new_password and confirm_password:
                    if new_password == confirm_password:
                        user.set_password(new_password)  # Securely set new password
                        user.save()
                        messages.success(request, 'Password changed successfully! Please log in.')
                        return redirect('login')
                    else:
                        messages.error(request, 'Passwords do not match.')
                else:
                    messages.error(request, 'Please fill out all fields.')
            except CustomUser.DoesNotExist:
                messages.error(request, 'User with this email does not exist.')

    return render(request, 'auth_otp/change_password.html')






from django.shortcuts import render, redirect
from django.contrib import messages
from .utils import send_otp  # Ensure send_otp is correctly imported
from users.models import CustomUser  # Import CustomUser model

def send_otp_view(request):
    print('in send_otp_view() ')
    if request.method == 'POST':
        email = request.POST.get('email')
        if email:
            try:
                user = CustomUser.objects.get(email=email)  # Query CustomUser directly
                send_otp(email, request)  # Send OTP if user exists
                request.session['email'] = email  # Store email in session
                messages.success(request, 'OTP sent successfully!')
                return redirect('verify-otp')  # Redirect to OTP verification page
            except CustomUser.DoesNotExist:
                messages.error(request, 'User with this email does not exist.')
            except Exception as e:
                messages.error(request, f'Failed to send OTP: {e}')
    return render(request, 'auth_otp/send_otp.html')


# def verify_otp_view(request):
#     if request.method == 'POST':
#         entered_otp = request.POST.get('otp')
#         stored_otp = request.session.get('otp')

#         if entered_otp == stored_otp:
#             messages.success(request, 'OTP verified successfully!')
#             # Redirect to change password page
#             return redirect('change-password')
#         else:
#             messages.error(request, 'Invalid OTP. Please try again.')

#     return render(request, 'verify_otp.html')


from django.shortcuts import render, redirect
from django.contrib import messages
from django.views.decorators.csrf import csrf_protect  # Import CSRF protection
from .utils import send_otp  # Import the send_otp function

@csrf_protect  # Ensures CSRF protection for POST requests
def verify_otp_view(request):
    if request.method == 'POST':
        print(' in verify_otp_view()')
        entered_otp = request.POST.get('otp')
        stored_otp = request.session.get('otp')  # Ensure OTP is stored in session

        print('entered_otp : ' , entered_otp)
        print('stored_otp : ' , stored_otp)

        if entered_otp == stored_otp:
            messages.success(request, 'OTP verified successfully!')
            return redirect('change-password')  # Redirect to change password page
        else:
            messages.error(request, 'Invalid OTP. Please try again.')

    return render(request, 'auth_otp/verify_otp.html')


