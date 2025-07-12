import random
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from django.shortcuts import render, redirect
from django.contrib import messages
from django.conf import settings
from users.models import CustomUser
from .models import PasswordResetOTP


# Email configuration (use your existing settings)
sender_email = settings.EMAIL_HOST_USER
sender_password = settings.EMAIL_HOST_PASSWORD
smtp_server = settings.EMAIL_HOST
smtp_port = settings.EMAIL_PORT

def forgot_password(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        
        # Check if user exists
        if not CustomUser.objects.filter(email=email).exists():
            messages.error(request, 'No account found with this email address.')
            return render(request, 'forgot_password.html')
        
        # Generate 6-digit OTP
        otp = str(random.randint(100000, 999999))
        
        # Save OTP to database
        PasswordResetOTP.objects.update_or_create(
            email=email,
            defaults={'otp': otp, 'is_verified': False}
        )
        
        # Send OTP email
        send_otp_email(email, otp)
        
        messages.success(request, 'OTP has been sent to your email!')
        return render(request, 'auth_otp/forgot_password.html', {
            'show_otp_field': True,
            'email': email,
            'step': 2  # For the progress indicator
        })


    
    return render(request, 'auth_otp/forgot_password.html', {'step': 1})

def verify_otp(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        otp = request.POST.get('otp')
        user_entered_otp = otp
        
        try:
            otp_record = PasswordResetOTP.objects.get(email=email)
            
            # Check if OTP matches and is not expired (10 minutes)
            from django.utils import timezone
            from datetime import timedelta
            
            if (otp_record.otp == user_entered_otp and 
                timezone.now() < otp_record.created_at + timedelta(minutes=10)):
                otp_record.is_verified = True
                otp_record.save()
                
                messages.success(request, 'OTP verified successfully!')
                return render(request, 'auth_otp/forgot_password.html', {
                    'show_password_fields': True,
                    'email': email,
                    'step': 3
                })
            else:
                messages.error(request, 'Invalid or expired OTP!')
                return render(request, 'auth_otp/forgot_password.html', {
                    'show_otp_field': True,
                    'email': email,
                    'step': 2
                })
                
        except PasswordResetOTP.DoesNotExist:
            messages.error(request, 'Invalid request!')
            return redirect('auth_otp:forgot_password')
    
    return redirect('auth_otp:forgot_password')

def reset_password(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')
        
        # Validate passwords match
        if password != confirm_password:
            messages.error(request, 'Passwords do not match!')
            return render(request, 'auth_otp/forgot_password.html', {
                'show_password_fields': True,
                'email': email,
                'step': 3
            })
        
        # Validate password strength (add more checks as needed)
        if len(password) < 8:
            messages.error(request, 'Password must be at least 8 characters long!')
            return render(request, 'forgot_password.html', {
                'show_password_fields': True,
                'email': email,
                'step': 3
            })
        
        try:
            # Verify OTP was actually verified
            otp_record = PasswordResetOTP.objects.get(email=email, is_verified=True)
            user = CustomUser.objects.get(email=email)
            
            # Update user's password using set_password (hashes automatically)
            user.set_password(password)
            user.save()
            
            # Delete the OTP record
            otp_record.delete()
            
            messages.success(request, 'Password reset successfully! You can now login with your new password.')
            return redirect('users:login')
            
        except (PasswordResetOTP.DoesNotExist, CustomUser.DoesNotExist):
            messages.error(request, 'Invalid request or session expired!')
            return redirect('auth_otp:forgot_password')
    
    return redirect('forgot_password')

def send_otp_email(email, otp):
    """Send OTP email using your existing email infrastructure"""
    print('\n--------Sending OTP Email-----------')
    print('Recipient:', email)

    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = email
    msg['Subject'] = "COEP Venue Booking - Password Reset OTP"

    # HTML email content
    body = f"""
    <html>
    <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
        <div style="max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #ddd; border-radius: 5px;">
            <h2 style="color: #1a73e8;">Password Reset Request</h2>
            <p>Dear User,</p>
            
            <p>We received a request to reset your password for the COEP Venue Booking System.</p>
            
            <div style="background: #f5f5f5; padding: 15px; border-radius: 5px; margin: 20px 0; text-align: center;">
                <h3 style="margin: 0; color: #1a73e8;">Your One-Time Password (OTP):</h3>
                <div style="font-size: 24px; font-weight: bold; letter-spacing: 2px; margin: 10px 0;">{otp}</div>
                <p style="font-size: 12px; color: #666;">(Valid for 10 minutes)</p>
            </div>
            
            <p>If you didn't request this password reset, please ignore this email or contact support immediately.</p>
            
            <p style="margin-top: 30px;">Regards,<br>
            <strong>COEP Venue Booking System</strong></p>
            
            <hr style="border: none; border-top: 1px solid #eee; margin: 20px 0;">
            <p style="font-size: 12px; color: #999;">
                This is an automated message. Please do not reply directly to this email.
            </p>
        </div>
    </body>
    </html>
    """

    msg.attach(MIMEText(body, 'html'))

    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.send_message(msg)
        print(f"OTP email sent successfully to {email}")
    except Exception as e:
        print(f"Failed to send email: {str(e)}")

    print('-----Email sending complete--------\n')