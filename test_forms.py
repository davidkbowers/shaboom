from django.test import TestCase, RequestFactory
from accounts.forms import CustomUserCreationForm, CustomAuthenticationForm, CustomPasswordChangeForm
from django.contrib.auth import get_user_model

User = get_user_model()

class TestCustomUserCreationForm(TestCase):
    def setUp(self):
        self.valid_member_data = {
            'email': 'member@example.com',
            'first_name': 'John',
            'last_name': 'Doe',
            'user_type': 'member',
            'password1': 'securepass123',
            'password2': 'securepass123'
        }
        
        self.valid_owner_data = {
            'email': 'owner@example.com',
            'first_name': 'Jane',
            'last_name': 'Smith',
            'user_type': 'owner',
            'gym_name': 'Fitness Plus',
            'phone_number': '123-456-7890',
            'address': '123 Gym Street',
            'password1': 'securepass123',
            'password2': 'securepass123'
        }

    def test_valid_member_registration(self):
        form = CustomUserCreationForm(data=self.valid_member_data)
        self.assertTrue(form.is_valid())

    def test_valid_owner_registration(self):
        form = CustomUserCreationForm(data=self.valid_owner_data)
        self.assertTrue(form.is_valid())

    def test_missing_gym_name_for_owner(self):
        data = self.valid_owner_data.copy()
        data['gym_name'] = ''
        form = CustomUserCreationForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('gym_name', form.errors)
        self.assertEqual(form.errors['gym_name'], ['Gym name is required for gym owners'])

    def test_invalid_email(self):
        data = self.valid_member_data.copy()
        data['email'] = 'invalid-email'
        form = CustomUserCreationForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)

    def test_password_mismatch(self):
        data = self.valid_member_data.copy()
        data['password2'] = 'differentpass123'
        form = CustomUserCreationForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('password2', form.errors)

    def test_required_fields(self):
        form = CustomUserCreationForm(data={})
        self.assertFalse(form.is_valid())
        required_fields = ['email', 'first_name', 'last_name', 'password1', 'password2']
        for field in required_fields:
            self.assertIn(field, form.errors)

class TestCustomAuthenticationForm(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123'
        )
        self.valid_data = {
            'username': 'test@example.com',
            'password': 'testpass123'
        }

    def test_valid_authentication(self):
        request = self.factory.get('/')
        form = CustomAuthenticationForm(request=request, data=self.valid_data)
        self.assertTrue(form.is_valid())

    def test_invalid_credentials(self):
        request = self.factory.get('/')
        data = self.valid_data.copy()
        data['password'] = 'wrongpass'
        form = CustomAuthenticationForm(request=request, data=data)
        self.assertFalse(form.is_valid())
        self.assertEqual(str(form.errors['__all__'][0]), str(form.error_messages['invalid_login']))

    def test_inactive_user(self):
        request = self.factory.get('/')
        # First verify the user can log in when active
        form = CustomAuthenticationForm(request=request, data=self.valid_data)
        self.assertTrue(form.is_valid())
        
        # Deactivate the user
        self.user.is_active = False
        self.user.save()
        
        # Verify authentication fails for inactive user
        form = CustomAuthenticationForm(request=request, data=self.valid_data)
        self.assertFalse(form.is_valid())
        self.assertTrue(len(form.errors['__all__']) > 0)  # Verify there is an error message

if __name__ == '__main__':
    unittest.main()
