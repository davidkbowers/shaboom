from django import forms
from studio.models import StudioProfile, StudioMembership
from django.core.exceptions import ValidationError

class StudioProfileForm(forms.ModelForm):
    subdomain = forms.SlugField(
        required=True,
        help_text="Choose a unique subdomain for your studio (e.g., 'yourstudio' for yourstudio.example.com)",
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'yourstudio'
        })
    )
    
    class Meta:
        model = StudioProfile
        fields = ['subdomain', 'logo', 'description', 'website', 'instagram', 'facebook']
        widgets = {
            'description': forms.Textarea(attrs={
                'class': 'form-input',
                'rows': 4,
                'placeholder': 'Tell potential members about your studio...'
            }),
            'website': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'www.yourstudio.com'
            }),
            'instagram': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'username'
            }),
            'facebook': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'page-name'
            }),
            'logo': forms.FileInput(attrs={
                'class': 'sr-only',
                'accept': 'image/*'
            })
        }

    def clean_subdomain(self):
        subdomain = self.cleaned_data.get('subdomain', '').lower()
        
        # Check if subdomain is already taken
        if StudioProfile.objects.filter(subdomain=subdomain).exists():
            if not (self.instance and self.instance.subdomain == subdomain):
                raise forms.ValidationError("This subdomain is already taken. Please choose another one.")
        
        # Validate subdomain format
        if not subdomain.isalnum() and '-' not in subdomain:
            raise forms.ValidationError("Subdomain can only contain letters, numbers, and hyphens.")
            
        # Prevent common subdomains that might conflict with system routes
        reserved_names = ['www', 'api', 'admin', 'app', 'staging', 'dev', 'test', 'mail', 'email', 'blog']
        if subdomain in reserved_names:
            raise forms.ValidationError("This subdomain is reserved. Please choose another one.")
            
        return subdomain
        
    def clean_website(self):
        website = self.cleaned_data.get('website', '')
        if website:
            # Remove http:// or https:// if present
            if website.startswith(('http://', 'https://')):
                website = website.split('://', 1)[1]
            # Remove www. if present
            if website.startswith('www.'):
                website = website[4:]
        return website

    def clean_instagram(self):
        instagram = self.cleaned_data.get('instagram', '')
        if instagram:
            # Remove @ if present
            if instagram.startswith('@'):
                instagram = instagram[1:]
            # Remove instagram.com/ if present
            if 'instagram.com/' in instagram:
                instagram = instagram.split('instagram.com/', 1)[1]
        return instagram

    def clean_facebook(self):
        facebook = self.cleaned_data.get('facebook', '')
        if facebook:
            # Remove facebook.com/ if present
            if 'facebook.com/' in facebook:
                facebook = facebook.split('facebook.com/', 1)[1]
        return facebook

class BusinessHoursForm(forms.Form):
    DAYS_OF_WEEK = [
        ('monday', 'Monday'),
        ('tuesday', 'Tuesday'),
        ('wednesday', 'Wednesday'),
        ('thursday', 'Thursday'),
        ('friday', 'Friday'),
        ('saturday', 'Saturday'),
        ('sunday', 'Sunday'),
    ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for day, label in self.DAYS_OF_WEEK:
            self.fields[f'{day}_open'] = forms.TimeField(
                required=False,
                widget=forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
                label=f'{label} Open'
            )
            self.fields[f'{day}_close'] = forms.TimeField(
                required=False,
                widget=forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
                label=f'{label} Close'
            )

    def clean(self):
        cleaned_data = super().clean()
        for day, _ in self.DAYS_OF_WEEK:
            open_time = cleaned_data.get(f'{day}_open')
            close_time = cleaned_data.get(f'{day}_close')
            
            if (open_time and not close_time) or (close_time and not open_time):
                raise ValidationError(f"Both opening and closing times must be set for {day}")
            
            if open_time and close_time and open_time >= close_time:
                raise ValidationError(f"Opening time must be before closing time for {day}")
        
        return cleaned_data

class SocialMediaForm(forms.ModelForm):
    facebook = forms.URLField(required=False, widget=forms.URLInput(attrs={'class': 'form-control'}))
    instagram = forms.URLField(required=False, widget=forms.URLInput(attrs={'class': 'form-control'}))
    twitter = forms.URLField(required=False, widget=forms.URLInput(attrs={'class': 'form-control'}))
    youtube = forms.URLField(required=False, widget=forms.URLInput(attrs={'class': 'form-control'}))
    linkedin = forms.URLField(required=False, widget=forms.URLInput(attrs={'class': 'form-control'}))
