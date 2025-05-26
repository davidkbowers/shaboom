from django.test import TestCase, Client
from django.urls import reverse, NoReverseMatch
from django.contrib.auth import get_user_model
from studio.models import StudioProfile

User = get_user_model()


class URLResolutionTest(TestCase):
    """Test suite dedicated to ensuring URL namespaces resolve correctly."""
    
    def setUp(self):
        # Create test users
        self.owner_user = User.objects.create_user(
            email='studio_owner@example.com',
            password='testpass123',
            user_type='owner'
        )
        
        self.member_user = User.objects.create_user(
            email='member@example.com',
            password='testpass123',
            user_type='member'
        )
        
        # Create a studio profile for the owner
        self.studio_profile = StudioProfile.objects.create(
            owner=self.owner_user,
            description='Test Studio Description',
            slug='test-studio'
        )
        
        self.client = Client()
    
    def test_public_urls_resolve(self):
        """Test that all public URLs resolve correctly."""
        # List of all public URL names with any required args
        public_urls = [
            ('public:landing', []),
            ('public:signup', []),
            ('public:login', []),
            ('public:logout', []),
            ('public:password_reset', []),
            ('public:password_reset_done', []),
            ('public:password_reset_confirm', ['MQ', 'test-token']),  # Dummy uidb64 and token
            ('public:password_reset_complete', []),
            ('public:plan_selection', []),
            ('public:studio_signup', ['test-studio']),  # Using the studio slug
        ]
        
        # Try to reverse each URL
        for name, args in public_urls:
            try:
                url = reverse(name, args=args)
                self.assertTrue(url.startswith('/'))  # URL should be valid
                print(f"✓ Successfully resolved {name} to {url}")
            except NoReverseMatch as e:
                self.fail(f"Failed to reverse URL {name}: {e}")
    
    def test_accounts_urls_resolve(self):
        """Test that all account URLs resolve correctly."""
        # List of all account URL names with any required args
        account_urls = [
            ('accounts:login', []),
            ('accounts:logout', []),
            ('accounts:register', []),
            ('accounts:password_change', []),
            ('accounts:studio:studio_profile_setup', []),
            ('accounts:studio:studio_dashboard', []),
            ('accounts:studio:studio_admin_dashboard', []),
            ('accounts:studio:toggle_public_videos', []),
            ('accounts:studio:toggle_public_signup', []),
        ]
        
        # Try to reverse each URL
        for name, args in account_urls:
            try:
                url = reverse(name, args=args)
                self.assertTrue(url.startswith('/'))  # URL should be valid
                print(f"✓ Successfully resolved {name} to {url}")
            except NoReverseMatch as e:
                self.fail(f"Failed to reverse URL {name}: {e}")
    
    def test_studio_urls_resolve(self):
        """Test that all studio URLs resolve correctly."""
        # List of all studio URL names with any required args
        studio_urls = [
            ('studio:dashboard', []),
            # Add other studio URLs as they are added to the app
        ]
        
        # Try to reverse each URL
        for name, args in studio_urls:
            try:
                url = reverse(name, args=args)
                self.assertTrue(url.startswith('/'))  # URL should be valid
                print(f"✓ Successfully resolved {name} to {url}")
            except NoReverseMatch as e:
                self.fail(f"Failed to reverse URL {name}: {e}")
    
    def test_videos_urls_resolve(self):
        """Test that all video URLs resolve correctly."""
        # List of all video URL names with any required args
        video_urls = [
            ('videos:upload_video', []),
            ('videos:video_list', []),
            ('videos:video_detail', [1]),  # Using dummy video ID
            ('videos:video_stream', [1, 'hd']),  # Using dummy video ID and quality
            ('videos:add_comment', [1]),  # Using dummy video ID
            ('videos:category_list', []),
            ('videos:category_detail', [1]),  # Using dummy category ID
            ('videos:playlist_list', []),
            ('videos:playlist_detail', [1]),  # Using dummy playlist ID
            ('videos:playlist_video_reorder', [1]),  # Using dummy playlist ID
            ('videos:playlist_video_remove', [1, 1]),  # Using dummy playlist and video IDs
            ('videos:student_video_list', []),
            ('videos:studio_video_list', [1]),  # Using dummy studio ID
        ]
        
        # Try to reverse each URL
        for name, args in video_urls:
            try:
                url = reverse(name, args=args)
                self.assertTrue(url.startswith('/'))  # URL should be valid
                print(f"✓ Successfully resolved {name} to {url}")
            except NoReverseMatch as e:
                self.fail(f"Failed to reverse URL {name}: {e}")
    
    def test_common_redirect_patterns(self):
        """Test that common redirect patterns in views resolve correctly."""
        redirect_patterns = [
            # Format: (view name, is_authenticated, is_studio_owner)
            # Note: accounts:profile doesn't exist currently and should be created
            # ('accounts:profile', True, False),
            ('studio:dashboard', True, True),
            ('public:login', False, False),
            ('public:signup', False, False),
            ('accounts:studio:studio_profile_setup', True, True),
        ]
        
        for name, is_auth, is_owner in redirect_patterns:
            try:
                url = reverse(name)
                self.assertTrue(url.startswith('/'))
                
                # Test access (simple GET request)
                if is_auth:
                    self.client.login(
                        email=self.owner_user.email if is_owner else self.member_user.email,
                        password='testpass123'
                    )
                    response = self.client.get(url)
                    self.assertNotEqual(response.status_code, 404)
                    
                    # Logout for next iteration
                    self.client.logout()
                
                print(f"✓ Successfully tested redirect pattern {name}")
            except NoReverseMatch as e:
                self.fail(f"Failed to reverse URL {name}: {e}")
