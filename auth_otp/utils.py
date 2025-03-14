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
