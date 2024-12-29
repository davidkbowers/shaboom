from django.test import TestCase
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.utils import timezone
from accounts.models import CustomUser, GymProfile, GymLocation, GymMembership
import json
from datetime import date

class CustomUserTests(TestCase):
    def setUp(self):
        self.user_data = {
            'email': 'test@example.com',
            'password': 'testpass123',
            'first_name': 'Test',
            'last_name': 'User'
        }
        
    def test_create_user(self):
        user = CustomUser.objects.create_user(**self.user_data)
        self.assertEqual(user.email, self.user_data['email'])
        self.assertTrue(user.check_password(self.user_data['password']))
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)
        
    def test_create_superuser(self):
        admin_user = CustomUser.objects.create_superuser(**self.user_data)
        self.assertEqual(admin_user.email, self.user_data['email'])
        self.assertTrue(admin_user.is_staff)
        self.assertTrue(admin_user.is_superuser)
        
    def test_email_required(self):
        self.user_data['email'] = ''
        with self.assertRaises(ValueError):
            CustomUser.objects.create_user(**self.user_data)
            
    def test_user_type_choices(self):
        user = CustomUser.objects.create_user(**self.user_data)
        self.assertEqual(user.user_type, 'member')  # Test default value
        
        user.user_type = 'owner'
        user.save()
        self.assertEqual(user.user_type, 'owner')
        
    def test_is_gym_owner_property(self):
        user = CustomUser.objects.create_user(**self.user_data)
        self.assertFalse(user.is_gym_owner)
        
        user.user_type = 'owner'
        user.save()
        self.assertTrue(user.is_gym_owner)

class GymProfileTests(TestCase):
    def setUp(self):
        self.owner = CustomUser.objects.create_user(
            email='gym@example.com',
            password='testpass123',
            user_type='owner'
        )
        self.profile_data = {
            'owner': self.owner,
            'business_name': 'Test Gym',
            'business_description': 'A test gym',
            'website': 'http://testgym.com',
            'business_hours': {
                'monday': '9:00-17:00',
                'tuesday': '9:00-17:00'
            },
            'amenities': ['wifi', 'parking'],
            'social_media': {
                'facebook': 'testgym',
                'instagram': 'testgym'
            }
        }
        
    def test_create_gym_profile(self):
        profile = GymProfile.objects.create(**self.profile_data)
        self.assertEqual(profile.business_name, 'Test Gym')
        self.assertEqual(profile.owner, self.owner)
        
    def test_gym_profile_str_method(self):
        profile = GymProfile.objects.create(**self.profile_data)
        expected_str = f"Test Gym - {self.owner.email}"
        self.assertEqual(str(profile), expected_str)
        
    def test_json_fields(self):
        profile = GymProfile.objects.create(**self.profile_data)
        self.assertTrue(isinstance(profile.business_hours, dict))
        self.assertTrue(isinstance(profile.amenities, list))
        self.assertTrue(isinstance(profile.social_media, dict))

class GymLocationTests(TestCase):
    def setUp(self):
        self.owner = CustomUser.objects.create_user(
            email='gym@example.com',
            password='testpass123',
            user_type='owner'
        )
        self.gym_profile = GymProfile.objects.create(
            owner=self.owner,
            business_name='Test Gym',
            business_description='A test gym'
        )
        self.location_data = {
            'gym': self.gym_profile,
            'name': 'Main Branch',
            'address': '123 Test St',
            'phone': '1234567890',
            'email': 'branch@testgym.com',
            'is_main_location': True
        }
        
    def test_create_location(self):
        location = GymLocation.objects.create(**self.location_data)
        self.assertEqual(location.name, 'Main Branch')
        self.assertEqual(location.gym, self.gym_profile)
        
    def test_unique_main_location(self):
        # Create first main location
        GymLocation.objects.create(**self.location_data)
        
        # Try to create another main location for the same gym
        self.location_data['name'] = 'Second Branch'
        with self.assertRaises(IntegrityError):
            GymLocation.objects.create(**self.location_data)
            
    def test_location_str_method(self):
        location = GymLocation.objects.create(**self.location_data)
        expected_str = f"Main Branch - {self.gym_profile.business_name}"
        self.assertEqual(str(location), expected_str)

class GymMembershipTests(TestCase):
    def setUp(self):
        self.owner = CustomUser.objects.create_user(
            email='gym@example.com',
            password='testpass123',
            user_type='owner'
        )
        self.member = CustomUser.objects.create_user(
            email='member@example.com',
            password='testpass123',
            user_type='member'
        )
        self.gym_profile = GymProfile.objects.create(
            owner=self.owner,
            business_name='Test Gym',
            business_description='A test gym'
        )
        self.membership_data = {
            'gym': self.gym_profile,
            'member': self.member,
            'status': 'pending'
        }
        
    def test_create_membership(self):
        membership = GymMembership.objects.create(**self.membership_data)
        self.assertEqual(membership.status, 'pending')
        self.assertEqual(membership.gym, self.gym_profile)
        self.assertEqual(membership.member, self.member)
        
    def test_membership_status_choices(self):
        membership = GymMembership.objects.create(**self.membership_data)
        
        # Test status changes
        valid_statuses = ['active', 'inactive', 'pending']
        for status in valid_statuses:
            membership.status = status
            membership.save()
            self.assertEqual(membership.status, status)
