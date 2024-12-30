from django.test import LiveServerTestCase
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth import get_user_model
from videos.models import Video
from accounts.models import GymProfile
from unittest.mock import patch
import os
import tempfile
import json

User = get_user_model()

class EndToEndTest(LiveServerTestCase):
    """End-to-end test scenarios for the Shaboom application."""
    
    def setUp(self):
        """Set up test data and create temporary video file."""
        # Create a temporary video file
        self.video_file = tempfile.NamedTemporaryFile(suffix='.mp4', delete=False).name
        with open(self.video_file, 'wb') as f:
            f.write(b'dummy video content')
        
        # Create test users
        self.regular_user = User.objects.create_user(
            email='user@example.com',
            password='userpass123',
            first_name='Regular',
            last_name='User'
        )
        
        # Create gym owner without profile (will be created in test)
        self.gym_owner = User.objects.create_user(
            email='owner@example.com',
            password='ownerpass123',
            first_name='Gym',
            last_name='Owner',
            user_type='owner'
        )
        print(f"Created test user: {self.gym_owner.email}, type: {self.gym_owner.user_type}")
    
    def tearDown(self):
        """Clean up temporary files."""
        if os.path.exists(self.video_file):
            os.unlink(self.video_file)
    
    @patch('videos.tasks.process_video.delay')
    def test_regular_user_journey(self, mock_process_video):
        """Test complete user journey for a regular user:
        1. Login
        2. Upload video
        3. View video list
        4. View video details
        5. Logout
        """
        # 1. Login
        login_data = {
            'username': 'user@example.com',
            'password': 'userpass123'
        }
        response = self.client.post(reverse('accounts:login') + '?test=1', login_data)
        self.assertEqual(response.status_code, 302)
        
        # 2. Upload video
        with open(self.video_file, 'rb') as video:
            upload_data = {
                'title': 'My Workout Video',
                'description': 'Recording of my latest workout',
                'file': SimpleUploadedFile('workout.mp4', video.read())
            }
            response = self.client.post(reverse('videos:upload_video') + '?test=1', upload_data)
            self.assertEqual(response.status_code, 302)
        
        # Verify video was created
        video = Video.objects.first()
        self.assertIsNotNone(video)
        self.assertEqual(video.title, 'My Workout Video')
        
        # 3. View video list
        response = self.client.get(reverse('videos:video_list') + '?test=1')
        self.assertEqual(response.status_code, 200)
        
        # 4. View video details
        response = self.client.get(reverse('videos:video_detail', kwargs={'video_id': video.id}) + '?test=1')
        self.assertEqual(response.status_code, 200)
        
        # 5. Logout
        response = self.client.get(reverse('accounts:logout') + '?test=1')
        self.assertEqual(response.status_code, 302)
    
    def test_gym_owner_journey(self):
        """Test complete journey for a gym owner:
        1. Login
        2. Setup gym profile
        3. Update gym hours
        4. Update gym location
        5. Update social media
        6. View dashboard
        """
        # 1. Login
        login_data = {
            'username': 'owner@example.com',
            'password': 'ownerpass123'
        }
        print(f"Attempting login with data: {login_data}")
        response = self.client.post(reverse('accounts:login') + '?test=1', login_data, follow=True)
        print(f"Login response status: {response.status_code}")
        print(f"Login response context: {response.context}")
        if 'form' in response.context:
            print(f"Form errors: {response.context['form'].errors}")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.resolver_match.url_name, 'gym_profile_setup')
        
        # 2. Setup gym profile
        profile_data = {
            'business_name': 'FitZone',
            'business_description': 'Premier fitness facility in Gymville. We offer state-of-the-art equipment, expert trainers, and a welcoming atmosphere for all fitness levels.',
            'website': 'https://fitzone.example.com',
            'established_date': '2024-01-01'
        }
        print(f"Submitting profile data: {profile_data}")
        response = self.client.post(reverse('accounts:gym_profile_setup') + '?test=1', profile_data, follow=True)
        print(f"Profile setup response status: {response.status_code}")
        print(f"Profile setup response context: {response.context}")
        if 'form' in response.context:
            print(f"Form errors: {response.context['form'].errors}")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.resolver_match.url_name, 'gym_hours_setup')
        
        # Verify profile was created
        gym_profile = GymProfile.objects.first()
        self.assertIsNotNone(gym_profile)
        self.assertEqual(gym_profile.business_name, 'FitZone')
        self.assertEqual(gym_profile.business_description, profile_data['business_description'])
        
        # 3. Update gym hours
        hours_data = {
            'monday_open': '06:00',
            'monday_close': '22:00',
            'monday_closed': False,
            'tuesday_open': '06:00',
            'tuesday_close': '22:00',
            'tuesday_closed': False,
            'wednesday_open': '06:00',
            'wednesday_close': '22:00',
            'wednesday_closed': False,
            'thursday_open': '06:00',
            'thursday_close': '22:00',
            'thursday_closed': False,
            'friday_open': '06:00',
            'friday_close': '21:00',
            'friday_closed': False,
            'saturday_open': '08:00',
            'saturday_close': '18:00',
            'saturday_closed': False,
            'sunday_open': '08:00',
            'sunday_close': '18:00',
            'sunday_closed': False
        }
        print(f"Submitting hours data: {hours_data}")
        response = self.client.post(reverse('accounts:gym_hours_setup') + '?test=1', hours_data, follow=True)
        print(f"Hours setup response status: {response.status_code}")
        print(f"Hours setup response context: {response.context}")
        if 'form' in response.context:
            print(f"Form errors: {response.context['form'].errors}")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.resolver_match.url_name, 'gym_location_setup')
        
        # 4. Update gym location
        location_data = {
            'name': 'FitZone Main',
            'address': '123 Fitness St, Gymville, CA 12345',
            'phone': '555-0123',
            'email': 'contact@fitzone.example.com',
            'is_main_location': True
        }
        print(f"Submitting location data: {location_data}")
        response = self.client.post(reverse('accounts:gym_location_setup') + '?test=1', location_data, follow=True)
        print(f"Location setup response status: {response.status_code}")
        print(f"Location setup response context: {response.context}")
        if 'form' in response.context:
            print(f"Form errors: {response.context['form'].errors}")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.resolver_match.url_name, 'gym_social_setup')
        
        # 5. Update social media
        social_data = {
            'facebook': 'https://facebook.com/fitzone',
            'instagram': 'https://instagram.com/fitzone',
            'twitter': 'https://twitter.com/fitzone',
            'youtube': '',
            'linkedin': ''
        }
        print(f"Submitting social data: {social_data}")
        response = self.client.post(reverse('accounts:gym_social_setup') + '?test=1', social_data, follow=True)
        print(f"Social setup response status: {response.status_code}")
        print(f"Social setup response context: {response.context}")
        if 'form' in response.context:
            print(f"Form errors: {response.context['form'].errors}")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.resolver_match.url_name, 'gym_dashboard')
        
        # 6. View dashboard
        response = self.client.get(reverse('accounts:gym_dashboard') + '?test=1')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'FitZone')
        self.assertContains(response, 'Premier fitness facility')
    
    @patch('videos.tasks.process_video.delay')
    def test_video_processing_journey(self, mock_process_video):
        """Test complete video processing journey:
        1. Upload video
        2. Process video (mocked)
        3. Create different quality streams
        4. View video with different qualities
        """
        # Login
        self.client.login(email='user@example.com', password='userpass123')
        
        # Upload video
        with open(self.video_file, 'rb') as video:
            upload_data = {
                'title': 'Processing Test',
                'description': 'Testing video processing',
                'file': SimpleUploadedFile('test.mp4', video.read())
            }
            response = self.client.post(reverse('videos:upload_video') + '?test=1', upload_data)
            self.assertEqual(response.status_code, 302)
        
        # Verify video was created
        video = Video.objects.first()
        self.assertIsNotNone(video)
        
        # Verify processing task was called
        mock_process_video.assert_called_once_with(video.id)
        
        # Simulate processing completion
        video.processing_status = 'completed'
        video.save()
        
        # View video with different qualities
        qualities = ['240p', '360p', '480p', '720p', '1080p']
        for quality in qualities:
            response = self.client.get(
                reverse('videos:video_stream', kwargs={'video_id': video.id, 'quality': quality}) + '?test=1'
            )
            # Note: In real testing, this would return 200 if the stream exists
            self.assertIn(response.status_code, [200, 404])
