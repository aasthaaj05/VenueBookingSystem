import sys
import io
from datetime import datetime, time
from unittest.mock import patch, MagicMock
from django.test import TestCase, RequestFactory
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.contrib.messages.storage.fallback import FallbackStorage
from django.contrib.sessions.middleware import SessionMiddleware

# Import your models and views
from gymkhana.models import Venue
from request_booking.models import Request

from request_booking.views import process_booking  # Make sure to import the view you're testing

User = get_user_model()

class ProcessBookingTests(TestCase):
    def setUp(self):
        # Suppress all print() output during tests
        self._original_stdout = sys.stdout
        sys.stdout = io.StringIO()

        # Create a user
        self.user = User.objects.create_user(
            name='Test User',  # Add this line
            email='testuser@example.com',
            # username='testuser',
            password='testpass123'
        )

        # Create test venues
        self.venue = Venue.objects.create(
            venue_name="Test Venue",
            location="Test Location",
            capacity=100
        )
        
        self.alt_venue1 = Venue.objects.create(
            venue_name="Alt Venue 1",
            location="Alt Location 1",
            capacity=80
        )
        
        self.alt_venue2 = Venue.objects.create(
            venue_name="Alt Venue 2",
            location="Alt Location 2",
            capacity=120
        )

        # Request factory for creating request objects
        self.factory = RequestFactory()

    def tearDown(self):
        # Restore print() output after each test
        sys.stdout = self._original_stdout

    def print_result(self, name, passed):
        output = f"✅ Passed: {name}" if passed else f"❌ Failed: {name}"
        self._original_stdout.write(output + "\n")

    def setup_request(self, url, method='post', data=None):
        """Helper to set up a request with session and messages"""
        if method.lower() == 'post':
            request = self.factory.post(url, data=data)
        else:
            request = self.factory.get(url)
        
        # Add session
        middleware = SessionMiddleware(lambda req: None)
        middleware.process_request(request)
        request.session.save()
        
        # Add messages
        setattr(request, 'session', 'session')
        messages = FallbackStorage(request)
        setattr(request, '_messages', messages)
        
        # Set user
        request.user = self.user
        
        return request

    @patch('your_app.views.send_booking_request_email')
    @patch('your_app.views.send_forwarded_notification')
    def test_successful_booking_request(self, mock_forward_email, mock_booking_email):
        test_name = "test_successful_booking_request"
        try:
            # Prepare test data
            booking_data = {
                'eventType': 'Conference',
                'fullName': 'John Doe',
                'email': 'john@example.com',
                'organization_name': 'Test Org',
                'start_date': '2025-05-01',
                'start_time': '10:00',
                'end_time': '15:00',
                'phone': '1234567890',
                'guestCount': '50',
                'alternateVenue1': str(self.alt_venue1.id),
                'alternateVenue2': str(self.alt_venue2.id),
                'eventDetails': 'Test event details',
                'purpose': 'Test purpose'
            }
            
            # Set up the request
            url = reverse('process_booking')  # Replace with your actual URL name
            request = self.setup_request(url, data=booking_data)
            request.session['venue_name'] = self.venue.venue_name
            
            # Call the view
            response = process_booking(request)
            
            # Check that the booking was created
            self.assertTrue(Request.objects.filter(
                user=self.user,
                email='john@example.com',
                event_type='Conference'
            ).exists())
            
            # Check emails were sent
            mock_booking_email.assert_called_once()
            mock_forward_email.assert_called_once()
            
            # Check redirect
            self.assertEqual(response.url, reverse('request_booking:index'))
            
            self.print_result(test_name, True)
        except AssertionError:
            self.print_result(test_name, False)
            raise

    @patch('your_app.views.send_duplicate_request_email')
    def test_duplicate_booking_request(self, mock_duplicate_email):
        test_name = "test_duplicate_booking_request"
        try:
            # Create an existing booking request
            existing_request = Request.objects.create(
                user=self.user,
                email='john@example.com',
                phone_number='1234567890',
                event_type='Conference',
                additional_info='Test purpose',
                date=datetime.strptime('2025-05-01', "%Y-%m-%d").date(),
                time=10,  # 10:00 AM
                duration=5,  # 5 hours
                venue=self.venue,
                status='pending',
                need='Test Org',
                alternate_venue_1=self.alt_venue1,
                alternate_venue_2=self.alt_venue2,
                event_details='Test event details',
                guest_count=50
            )
            
            # Prepare duplicate request data
            booking_data = {
                'eventType': 'Conference',
                'fullName': 'John Doe',
                'email': 'john@example.com',
                'organization_name': 'Test Org',
                'start_date': '2025-05-01',
                'start_time': '10:00',
                'end_time': '15:00',
                'phone': '1234567890',
                'guestCount': '50',
                'alternateVenue1': str(self.alt_venue1.id),
                'alternateVenue2': str(self.alt_venue2.id),
                'eventDetails': 'Test event details',
                'purpose': 'Test purpose'
            }
            
            # Set up the request
            url = reverse('process_booking')  # Replace with your actual URL name
            request = self.setup_request(url, data=booking_data)
            request.session['venue_name'] = self.venue.venue_name
            
            # Call the view
            response = process_booking(request)
            
            # Check duplicate email was sent
            mock_duplicate_email.assert_called_once()
            
            # Check redirect
            self.assertEqual(response.url, reverse('request_booking:index'))
            
            self.print_result(test_name, True)
        except AssertionError:
            self.print_result(test_name, False)
            raise

    def test_invalid_venue_error(self):
        test_name = "test_invalid_venue_error"
        try:
            # Prepare test data with non-existent venue
            booking_data = {
                'eventType': 'Conference',
                'fullName': 'John Doe',
                'email': 'john@example.com',
                'organization_name': 'Test Org',
                'start_date': '2025-05-01',
                'start_time': '10:00',
                'end_time': '15:00',
                'phone': '1234567890',
                'guestCount': '50',
                'alternateVenue1': '999',  # Non-existent venue ID
                'alternateVenue2': str(self.alt_venue2.id),
                'eventDetails': 'Test event details',
                'purpose': 'Test purpose'
            }
            
            # Set up the request
            url = reverse('process_booking')  # Replace with your actual URL name
            request = self.setup_request(url, data=booking_data)
            request.session['venue_name'] = 'Non-existent Venue'
            
            # Call the view
            response = process_booking(request)
            
            # Check redirect to booking status
            self.assertEqual(response.url, reverse('request_booking:booking_status'))
            
            self.print_result(test_name, True)
        except AssertionError:
            self.print_result(test_name, False)
            raise

    def test_invalid_date_format(self):
        test_name = "test_invalid_date_format"
        try:
            # Prepare test data with invalid date format
            booking_data = {
                'eventType': 'Conference',
                'fullName': 'John Doe',
                'email': 'john@example.com',
                'organization_name': 'Test Org',
                'start_date': 'invalid-date',  # Invalid date format
                'start_time': '10:00',
                'end_time': '15:00',
                'phone': '1234567890',
                'guestCount': '50',
                'alternateVenue1': str(self.alt_venue1.id),
                'alternateVenue2': str(self.alt_venue2.id),
                'eventDetails': 'Test event details',
                'purpose': 'Test purpose'
            }
            
            # Set up the request
            url = reverse('process_booking')  # Replace with your actual URL name
            request = self.setup_request(url, data=booking_data)
            request.session['venue_name'] = self.venue.venue_name
            
            # Call the view
            response = process_booking(request)
            
            # Check redirect to booking status
            self.assertEqual(response.url, reverse('request_booking:booking_status'))
            
            self.print_result(test_name, True)
        except AssertionError:
            self.print_result(test_name, False)
            raise

    def test_invalid_time_format(self):
        test_name = "test_invalid_time_format"
        try:
            # Prepare test data with invalid time format
            booking_data = {
                'eventType': 'Conference',
                'fullName': 'John Doe',
                'email': 'john@example.com',
                'organization_name': 'Test Org',
                'start_date': '2025-05-01',
                'start_time': 'invalid-time',  # Invalid time format
                'end_time': '15:00',
                'phone': '1234567890',
                'guestCount': '50',
                'alternateVenue1': str(self.alt_venue1.id),
                'alternateVenue2': str(self.alt_venue2.id),
                'eventDetails': 'Test event details',
                'purpose': 'Test purpose'
            }
            
            # Set up the request
            url = reverse('process_booking')  # Replace with your actual URL name
            request = self.setup_request(url, data=booking_data)
            request.session['venue_name'] = self.venue.venue_name
            
            # Call the view
            response = process_booking(request)
            
            # Check redirect to booking status
            self.assertEqual(response.url, reverse('request_booking:booking_status'))
            
            self.print_result(test_name, True)
        except AssertionError:
            self.print_result(test_name, False)
            raise

    def test_non_post_request(self):
        test_name = "test_non_post_request"
        try:
            # Set up a GET request
            url = reverse('process_booking')  # Replace with your actual URL name
            request = self.setup_request(url, method='get')
            
            # Call the view
            response = process_booking(request)
            
            # Check redirect to booking status
            self.assertEqual(response.url, reverse('request_booking:booking_status'))
            
            self.print_result(test_name, True)
        except AssertionError:
            self.print_result(test_name, False)
            raise