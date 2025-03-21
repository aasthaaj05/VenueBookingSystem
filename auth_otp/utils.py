import random
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

def send_otp(email , request):
    # Generate a random 6-digit OTP
    otp = ''.join([str(random.randint(0, 9)) for _ in range(6)])

    request.session['otp'] = otp
    
    # Email configuration
    sender_email = ""           # Enter Outlook Email
    sender_password = ""        # Enter Outlook Email Password
    receiver_email = email
    smtp_server = "smtp.office365.com"
    smtp_port = 587  # Outlook.com SMTP port

    # Create message container
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg['Subject'] = "Password Reset OTP"

    # Email body
    body = f"Your OTP for password reset is: {otp}"
    msg.attach(MIMEText(body, 'plain'))

    # Connect to SMTP server
    with smtplib.SMTP(smtp_server, smtp_port) as server:
        server.starttls()  # Secure the connection
        server.login(sender_email, sender_password)
        server.send_message(msg)



import smtplib
import random
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

def send_venue_booking_confirmation(email, venue_name):
    sender_email = ""  # Enter Outlook Email
    sender_password = ""      # Enter Outlook Email Password
    receiver_email = email
    smtp_server = "smtp.office365.com"
    smtp_port = 587  # Outlook.com SMTP port

    # Create message container
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg['Subject'] = "Venue Booking Request Sent"

    # Email body
    body = f"Your request for venue booking for '{venue_name}' has been sent successfully. We will notify you once it is approved."
    msg.attach(MIMEText(body, 'plain'))

    # Connect to SMTP server and send email
    with smtplib.SMTP(smtp_server, smtp_port) as server:
        server.starttls()  # Secure the connection
        server.login(sender_email, sender_password)
        server.send_message(msg)

    print(f"Confirmation email sent to {email}")

# Example usage:
# send_venue_booking_confirmation("user@example.com", "COEP Seminar Hall")
