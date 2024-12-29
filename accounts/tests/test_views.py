from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.messages import get_messages
from accounts.models import CustomUser, GymProfile, GymLocation, GymMembership
from accounts.forms import CustomUserCreationForm, CustomAuthenticationForm
import json
from datetime import datetime

class BaseViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user_data = {
            'email': 'test@example.com',
            'password1': 'testpass123',
            'password2': 'testpass123',
            'first_name': 'Test',
            'last_name': 'User',
            'user_type': 'member',
            'gym_name': '',
            'phone_number': '',
            'address': ''
        }
        self.login_data = {
            'username': 'test@example.com',
            'password': 'testpass123'
        }
        self.gym_owner_data = {
            'email': 'gym@example.com',
            'password1': 'testpass123',
            'password2': 'testpass123',
            'first_name': 'Gym',
            'last_name': 'Owner',
            'user_type': 'owner',
            'gym_name': 'Test Gym',
            'phone_number': '1234567890',
            'address': '123 Test St'
        }

class AuthenticationViewsTest(BaseViewTest):
    def setUp(self):
        self.user_data = {
            'email': 'test@example.com',
            'password1': 'testpass123',
            'password2': 'testpass123',
            'first_name': 'Test',
            'last_name': 'User',
            'user_type': 'member'
        }
        self.login_data = {
            'username': 'test@example.com',
            'password': 'testpass123'
        }

    def test_register_view_get(self):
        response = self.client.get(reverse('register'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/register.html')
        self.assertIsInstance(response.context['form'], CustomUserCreationForm)

    def test_register_view_post_success(self):
        response = self.client.post(reverse('register'), self.user_data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('marketing:landing'))
        self.assertTrue(CustomUser.objects.filter(email=self.user_data['email']).exists())

    def test_register_view_post_success_gym_owner(self):
        gym_owner_data = self.user_data.copy()
        gym_owner_data.update({
            'user_type': 'owner',
            'gym_name': 'Test Gym',
            'phone_number': '123-456-7890',
            'address': '123 Test St'
        })
        response = self.client.post(reverse('register'), gym_owner_data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('gym_profile_setup'))
        self.assertTrue(CustomUser.objects.filter(email=gym_owner_data['email']).exists())

    def test_register_view_post_invalid(self):
        # Submit with mismatched passwords
        data = self.user_data.copy()
        data['password2'] = 'differentpass123'  # Different from password1
        response = self.client.post(reverse('register'), data)
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/register.html')
        self.assertContains(response, "The two password fields didn’t match.")

    def test_login_view_get(self):
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/login.html')
        self.assertIsInstance(response.context['form'], CustomAuthenticationForm)

    def test_login_view_post_success(self):
        # Create a user first
        CustomUser.objects.create_user(
            email=self.login_data['username'],
            password=self.login_data['password']
        )
        response = self.client.post(reverse('login'), self.login_data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('marketing:landing'))

    def test_login_view_post_success_gym_owner(self):
        # Create a gym owner user
        user = CustomUser.objects.create_user(
            email=self.login_data['username'],
            password=self.login_data['password'],
            user_type='owner'
        )
        # Create a gym profile for the owner
        GymProfile.objects.create(
            owner=user,
            business_name='Test Gym',
            business_description='A test gym'
        )
        response = self.client.post(reverse('login'), self.login_data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('gym_dashboard'))

    def test_login_view_post_invalid(self):
        response = self.client.post(reverse('login'), {
            'username': 'wrong@example.com',
            'password': 'wrongpass123'
        })
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/login.html')
        self.assertContains(response, "Invalid username or password")

    def test_logout_view(self):
        # Login first
        CustomUser.objects.create_user(
            email=self.login_data['username'],
            password=self.login_data['password']
        )
        self.client.login(**self.login_data)
        
        response = self.client.get(reverse('logout'))
        self.assertEqual(response.status_code, 302)

class GymOwnerViewsTest(TestCase):
    def setUp(self):
        # Create login data
        self.login_data = {
            'username': 'gym@example.com',
            'password': 'testpass123'
        }
        
        # Create a gym owner user
        self.gym_owner = CustomUser.objects.create_user(
            email=self.login_data['username'],
            password=self.login_data['password'],
            first_name='Gym',
            last_name='Owner',
            user_type='owner',  # This will make is_gym_owner True
            gym_name='Test Gym'
        )
        
        # Create test data
        self.gym_profile_data = {
            'business_name': 'Test Gym',
            'business_description': 'A test gym',
            'website': 'http://testgym.com',
            'established_date': '2023-01-01'
        }
        
        # Create GymProfile for the owner
        self.gym_profile = GymProfile.objects.create(
            owner=self.gym_owner,
            business_name=self.gym_profile_data['business_name'],
            business_description=self.gym_profile_data['business_description'],
            website=self.gym_profile_data['website'],
            established_date=self.gym_profile_data['established_date']
        )
        
        # Create client
        self.client = Client()
        
        self.location_data = {
            'name': 'Main Branch',
            'address': '123 Test St',
            'phone': '1234567890',
            'email': 'branch@testgym.com',
            'is_main_location': True
        }

    def test_gym_profile_setup_get(self):
        # Login first
        self.client.login(**self.login_data)
        response = self.client.get(reverse('gym_profile_setup'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/gym/profile_setup.html')

    def test_gym_profile_setup_post_success(self):
        # Login first
        self.client.login(**self.login_data)
        
        # Delete the GymProfile created in setUp since we're testing profile creation
        GymProfile.objects.filter(owner=self.gym_owner).delete()
        
        response = self.client.post(reverse('gym_profile_setup'), self.gym_profile_data)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(GymProfile.objects.filter(owner=self.gym_owner).exists())
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertIn('Gym profile created successfully!', str(messages[0]))

    def test_gym_profile_setup_post_invalid(self):
        # Login first
        self.client.login(**self.login_data)
        
        # Delete the GymProfile created in setUp since we're testing profile creation
        GymProfile.objects.filter(owner=self.gym_owner).delete()
        
        # Submit empty form
        response = self.client.post(reverse('gym_profile_setup'), {})
        
        # Check response
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/gym/profile_setup.html')
        
        # Check no profile was created
        with self.assertRaises(GymProfile.DoesNotExist):
            GymProfile.objects.get(owner=self.gym_owner)
        
        # Get the form from the response context
        form = response.context['form']
        self.assertTrue(form.errors)
        self.assertIn('business_name', form.errors)
        self.assertIn('business_description', form.errors)
        self.assertEqual(form.errors['business_name'][0], 'This field is required.')

    def test_gym_location_setup(self):
        # Login first
        self.client.login(**self.login_data)
        
        response = self.client.post(reverse('gym_location_setup'), self.location_data)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(GymLocation.objects.filter(gym=self.gym_profile).exists())
        messages = list(get_messages(response.wsgi_request))
        self.assertIn('Gym location added successfully!', str(messages[0]))

    def test_gym_hours_setup(self):
        # Login first
        self.client.login(**self.login_data)
        
        # Create a location first since it's required
        GymLocation.objects.create(
            gym=self.gym_profile,
            name=self.location_data['name'],
            address=self.location_data['address'],
            phone=self.location_data['phone'],
            email=self.location_data['email'],
            is_main_location=self.location_data['is_main_location']
        )
        
        # Test GET request
        response = self.client.get(reverse('gym_hours_setup'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/gym/hours_setup.html')
        
        # Test POST request with valid data for all days
        hours_data = {}
        for day in ['monday', 'tuesday', 'wednesday', 'thursday', 'friday']:
            hours_data.update({
                f'{day}_open': '09:00',
                f'{day}_close': '17:00',
                f'{day}_closed': ''
            })
        
        # Weekend days are closed
        for day in ['saturday', 'sunday']:
            hours_data.update({
                f'{day}_closed': 'on'
            })
        
        response = self.client.post(reverse('gym_hours_setup'), hours_data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('gym_social_setup'))
        
        # Verify data was saved
        self.gym_profile.refresh_from_db()
        self.assertTrue(self.gym_profile.business_hours)
        
        # Verify weekday hours
        for day in ['monday', 'tuesday', 'wednesday', 'thursday', 'friday']:
            self.assertEqual(self.gym_profile.business_hours[day]['open'], '09:00')
            self.assertEqual(self.gym_profile.business_hours[day]['close'], '17:00')
            self.assertFalse(self.gym_profile.business_hours[day]['closed'])
        
        # Verify weekend days are closed
        for day in ['saturday', 'sunday']:
            self.assertTrue(self.gym_profile.business_hours[day]['closed'])

    def test_gym_social_setup(self):
        # Login first
        self.client.login(**self.login_data)
        
        # Create a gym location
        GymLocation.objects.create(
            gym=self.gym_profile,
            name=self.location_data['name'],
            address=self.location_data['address'],
            phone=self.location_data['phone'],
            email=self.location_data['email'],
            is_main_location=self.location_data['is_main_location']
        )
        
        # Test GET request
        response = self.client.get(reverse('gym_social_setup'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/gym/social_setup.html')
        
        # Test POST request with valid data
        social_data = {
            'facebook': 'https://facebook.com/testgym',
            'instagram': 'https://instagram.com/testgym',
            'twitter': 'https://twitter.com/testgym',
            'youtube': '',  # Optional field
        }
        
        response = self.client.post(reverse('gym_social_setup'), social_data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('gym_dashboard'))
        
        # Verify data was saved
        self.gym_profile.refresh_from_db()
        self.assertTrue(self.gym_profile.social_media)
        self.assertEqual(self.gym_profile.social_media['facebook'], social_data['facebook'])
        
        # Verify onboarding completed
        self.gym_owner.refresh_from_db()
        self.assertTrue(self.gym_owner.onboarding_completed)

    def test_unauthorized_access(self):
        # Create a regular user
        regular_user = CustomUser.objects.create_user(
            email='user@example.com',
            password='testpass123',
            first_name='Regular',
            last_name='User',
            user_type='member'
        )
        
        # Try to access gym owner views with regular user
        self.client.force_login(regular_user)
        
        # Test each gym owner view
        views = ['gym_profile_setup', 'gym_location_setup', 'gym_hours_setup', 'gym_social_setup']
        for view_name in views:
            response = self.client.get(reverse(view_name))
            self.assertEqual(response.status_code, 302, f"Regular user should be redirected from {view_name}")
            self.assertTrue(response.url.startswith('/accounts/login/'), 
                          f"Regular user should be redirected to login from {view_name}")
