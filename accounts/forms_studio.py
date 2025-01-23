from django import forms
from .models import StudioProfile, StudioLocation
from django.core.exceptions import ValidationError

class StudioProfileForm(forms.ModelForm):
    class Meta:
        model = StudioProfile
        fields = ['business_name', 'business_description', 'website', 'logo', 'established_date']
        widgets = {
            'business_name': forms.TextInput(attrs={'class': 'form-control'}),
            'business_description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'website': forms.URLInput(attrs={'class': 'form-control'}),
            'established_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }

class StudioLocationForm(forms.ModelForm):
    class Meta:
        model = StudioLocation
        fields = ['name', 'address', 'phone', 'email', 'is_main_location']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'is_main_location': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

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
