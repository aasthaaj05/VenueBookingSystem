import sys
import io
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse

User = get_user_model()

class LoginViewTests(TestCase):
    def setUp(self):
        # Suppress all print() output during tests (including from views)
        self._original_stdout = sys.stdout
        sys.stdout = io.StringIO()

        self.client = Client()
        # Create users with different roles for testing
        self.faculty_advisor = User.objects.create_user(
            email='faculty_advisor@example.com',
            name='Faculty Advisor',
            password='testpass123',
            role='faculty_advisor'
        )
        
        self.venue_admin = User.objects.create_user(
            email='venue_admin@example.com',
            name='Venue Admin',
            password='testpass123',
            role='venue_admin'
        )
        
        self.faculty = User.objects.create_user(
            email='faculty@example.com',
            name='Faculty User',
            password='testpass123',
            role='faculty'
        )
        
        self.other_user = User.objects.create_user(
            email='other@example.com',
            name='Other User',
            password='testpass123',
            role='other_role'
        )
        
        self.login_url = reverse('login')

    def tearDown(self):
        # Restore print() output after each test
        sys.stdout = self._original_stdout

    def print_result(self, name, passed):
        output = f"✅ Passed: {name}" if passed else f"❌ Failed: {name}"
        self._original_stdout.write(output + "\n")

    def test_get_request_renders_login_template(self):
        test_name = "test_get_request_renders_login_template"
        try:
            response = self.client.get(self.login_url)
            self.assertEqual(response.status_code, 200)
            self.assertTemplateUsed(response, 'users/login.html')
            self.print_result(test_name, True)
        except AssertionError:
            self.print_result(test_name, False)
            raise

    def test_session_flushed_on_get_request(self):
        test_name = "test_session_flushed_on_get_request"
        try:
            # Set a session variable
            session = self.client.session
            session['test_key'] = 'test_value'
            session.save()
            
            # Make a GET request to login
            response = self.client.get(self.login_url)
            
            # Verify session is flushed
            self.assertEqual(response.status_code, 200)
            self.assertNotIn('test_key', self.client.session)
            self.print_result(test_name, True)
        except AssertionError:
            self.print_result(test_name, False)
            raise

    def test_invalid_credentials_returns_login_page(self):
        test_name = "test_invalid_credentials_returns_login_page"
        try:
            response = self.client.post(self.login_url, {
                'username': 'faculty_advisor@example.com',
                'password': 'wrongpassword'
            })
            self.assertEqual(response.status_code, 200)
            self.assertTemplateUsed(response, 'users/login.html')
            self.print_result(test_name, True)
        except AssertionError:
            self.print_result(test_name, False)
            raise

    def test_missing_credentials_returns_login_page(self):
        test_name = "test_missing_credentials_returns_login_page"
        try:
            response = self.client.post(self.login_url, {
                'username': '',
                'password': ''
            })
            self.assertEqual(response.status_code, 200)
            self.assertTemplateUsed(response, 'users/login.html')
            self.print_result(test_name, True)
        except AssertionError:
            self.print_result(test_name, False)
            raise

    def test_faculty_advisor_login_redirects_correctly(self):
        test_name = "test_faculty_advisor_login_redirects_correctly"
        try:
            response = self.client.post(self.login_url, {
                'username': 'faculty_advisor@example.com',
                'password': 'testpass123'
            })
            self.assertEqual(response.status_code, 302)
            self.assertEqual(response.url, '/faculty_advisor/home')
            self.print_result(test_name, True)
        except AssertionError:
            self.print_result(test_name, False)
            raise

    def test_venue_admin_login_redirects_correctly(self):
        test_name = "test_venue_admin_login_redirects_correctly"
        try:
            response = self.client.post(self.login_url, {
                'username': 'venue_admin@example.com',
                'password': 'testpass123'
            })
            self.assertEqual(response.status_code, 302)
            self.assertEqual(response.url, '/venue_admin/home')
            self.print_result(test_name, True)
        except AssertionError:
            self.print_result(test_name, False)
            raise

    def test_faculty_login_redirects_correctly(self):
        test_name = "test_faculty_login_redirects_correctly"
        try:
            response = self.client.post(self.login_url, {
                'username': 'faculty@example.com',
                'password': 'testpass123'
            })
            self.assertEqual(response.status_code, 302)
            self.assertEqual(response.url, '/faculty_advisor/home')
            self.print_result(test_name, True)
        except AssertionError:
            self.print_result(test_name, False)
            raise

    def test_other_role_redirects_to_login(self):
        test_name = "test_other_role_redirects_to_login"
        try:
            response = self.client.post(self.login_url, {
                'username': 'other@example.com',
                'password': 'testpass123'
            })
            self.assertEqual(response.status_code, 302)
            self.assertEqual(response.url, '/users/login')
            self.print_result(test_name, True)
        except AssertionError:
            self.print_result(test_name, False)
            raise

    def test_session_email_set_after_login(self):
        test_name = "test_session_email_set_after_login"
        try:
            response = self.client.post(self.login_url, {
                'username': 'faculty_advisor@example.com',
                'password': 'testpass123'
            }, follow=True)  # Follow redirects
            
            self.assertEqual(self.client.session['email'], 'faculty_advisor@example.com')
            self.print_result(test_name, True)
        except (AssertionError, KeyError):
            self.print_result(test_name, False)
            raise

    def test_user_authenticated_after_login(self):
        test_name = "test_user_authenticated_after_login"
        try:
            response = self.client.post(self.login_url, {
                'username': 'faculty_advisor@example.com',
                'password': 'testpass123'
            }, follow=True)  # Follow redirects
            
            self.assertTrue(response.context['user'].is_authenticated)
            self.print_result(test_name, True)
        except AssertionError:
            self.print_result(test_name, False)
            raise

    def test_case_insensitive_role_handling(self):
        test_name = "test_case_insensitive_role_handling"
        try:
            # Create user with capitalized role
            case_test_user = User.objects.create_user(
                email='case_test@example.com',
                name='Case Test User',
                password='testpass123',
                role='Faculty_advisor'  # Note capitalization
            )
            
            response = self.client.post(self.login_url, {
                'username': 'case_test@example.com',
                'password': 'testpass123'
            })
            
            self.assertEqual(response.status_code, 302)
            self.assertEqual(response.url, '/faculty_advisor/home')
            self.print_result(test_name, True)
        except AssertionError:
            self.print_result(test_name, False)
            raise