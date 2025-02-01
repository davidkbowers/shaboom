from django import forms
from .models import StudioProfile, StudioMembership
from django.core.exceptions import ValidationError

class StudioProfileForm(forms.ModelForm):
    class Meta:
        model = StudioProfile
        fields = ['website', 'logo']
        widgets = {
            'website': forms.URLInput(attrs={'class': 'form-control'}),
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
