from django.test import TestCase, Client
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth import get_user_model
from videos.models import Video
from accounts.models import GymProfile
import os
import tempfile
from unittest.mock import patch

User = get_user_model()

class UserVideoIntegrationTest(TestCase):
    def setUp(self):
        self.client = Client()
        # Create a test user
        self.user = User.objects.create_user(
            email='testuser@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User',
            user_type='member'
        )
        # Create a test video file
        self.video_file = tempfile.NamedTemporaryFile(suffix='.mp4').name
        with open(self.video_file, 'wb') as f:
            f.write(b'dummy video content')

    def tearDown(self):
        # Clean up the test video file
        if os.path.exists(self.video_file):
            os.remove(self.video_file)

    def test_user_registration_and_video_upload(self):
        # 1. Register a new user
        registration_data = {
            'email': 'newuser@example.com',
            'password1': 'securepass123',
            'password2': 'securepass123',
            'first_name': 'New',
            'last_name': 'User',
            'user_type': 'member'
        }
        response = self.client.post(reverse('accounts:register'), registration_data)
        self.assertEqual(response.status_code, 302)  # Should redirect after successful registration
        self.assertTrue(User.objects.filter(email='newuser@example.com').exists())

        # 2. Upload a video as the new user
        self.client.login(email='newuser@example.com', password='securepass123')
        with open(self.video_file, 'rb') as video:
            upload_data = {
                'title': 'Test Video',
                'description': 'Test Description',
                'file': SimpleUploadedFile('test.mp4', video.read())
            }
            response = self.client.post(reverse('videos:upload_video'), upload_data)
            self.assertEqual(response.status_code, 302)  # Should redirect after successful upload

        # 3. Verify video was created and associated with user
        video = Video.objects.first()
        self.assertIsNotNone(video)
        self.assertEqual(video.title, 'Test Video')
        self.assertEqual(video.uploaded_by.email, 'newuser@example.com')

class GymOwnerIntegrationTest(TestCase):
    def setUp(self):
        self.client = Client()
        # Create a gym owner
        self.gym_owner = User.objects.create_user(
            email='gym@example.com',
            password='gympass123',
            first_name='Gym',
            last_name='Owner',
            user_type='owner'
        )

    def test_gym_owner_registration_and_profile_setup(self):
        # 1. Register a new gym owner
        registration_data = {
            'email': 'newgym@example.com',
            'password1': 'securepass123',
            'password2': 'securepass123',
            'first_name': 'New',
            'last_name': 'Gym',
            'user_type': 'owner',
            'gym_name': 'Fitness Plus'
        }
        response = self.client.post(reverse('accounts:register'), registration_data)
        self.assertEqual(response.status_code, 302)  # Should redirect to profile setup

        # 2. Set up gym profile
        self.client.login(email='newgym@example.com', password='securepass123')
        profile_data = {
            'gym_name': 'Fitness Plus',
            'address': '123 Gym Street',
            'phone_number': '123-456-7890'
        }
        response = self.client.post(reverse('accounts:gym_profile_setup'), profile_data)
        self.assertEqual(response.status_code, 302)  # Should redirect to dashboard

        # 3. Verify gym profile was created
        gym_owner = User.objects.get(email='newgym@example.com')
        self.assertTrue(hasattr(gym_owner, 'gym_profile'))
        self.assertEqual(gym_owner.gym_profile.gym_name, 'Fitness Plus')

class AuthenticationFlowTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            email='testuser@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User',
            user_type='member'
        )
        self.video_file = tempfile.NamedTemporaryFile(suffix='.mp4').name
        with open(self.video_file, 'wb') as f:
            f.write(b'dummy video content')

    def tearDown(self):
        if os.path.exists(self.video_file):
            os.remove(self.video_file)

    def test_login_logout_flow(self):
        # 1. Test successful login
        login_data = {
            'username': 'testuser@example.com',
            'password': 'testpass123'
        }
        response = self.client.post(reverse('accounts:login'), login_data)
        self.assertEqual(response.status_code, 302)  # Should redirect after login
        
        # 2. Test accessing protected view (using test template)
        response = self.client.get(reverse('videos:video_list') + '?test=1')
        self.assertEqual(response.status_code, 200)  # Should be able to access
        
        # 3. Test logout
        response = self.client.get(reverse('accounts:logout'))
        self.assertEqual(response.status_code, 302)  # Should redirect after logout
        
        # 4. Test accessing protected view after logout (using test template)
        response = self.client.get(reverse('videos:video_list') + '?test=1')
        self.assertEqual(response.status_code, 302)  # Should redirect to login

    @patch('videos.views.VideoFileClip')
    @patch('videos.tasks.process_video.delay')
    def test_video_processing_flow(self, mock_process_video_delay, mock_video_file_clip):
        # Mock video duration
        mock_video_file_clip.return_value.__enter__.return_value.duration = 30

        # 1. Login
        self.client.login(email='testuser@example.com', password='testpass123')

        # 2. Upload video
        with open(self.video_file, 'rb') as video:
            upload_data = {
                'title': 'Process Test Video',
                'description': 'Testing video processing',
                'file': SimpleUploadedFile('test.mp4', video.read())
            }
            response = self.client.post(reverse('videos:upload_video'), upload_data)
            self.assertEqual(response.status_code, 302)

        # 3. Verify processing task was called
        video = Video.objects.first()
        mock_process_video_delay.assert_called_once_with(video.id)

        # 4. Verify video metadata was updated
        self.assertEqual(video.duration, 30)
        self.assertTrue(video.size > 0)
