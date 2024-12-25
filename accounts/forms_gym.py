from django import forms
from .models import GymProfile, GymLocation
from django.core.exceptions import ValidationError

class GymProfileForm(forms.ModelForm):
    class Meta:
        model = GymProfile
        fields = ['business_name', 'business_description', 'website', 'logo', 'established_date']
        widgets = {
            'business_name': forms.TextInput(attrs={'class': 'form-control'}),
            'business_description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'website': forms.URLInput(attrs={'class': 'form-control'}),
            'established_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }

class GymLocationForm(forms.ModelForm):
    class Meta:
        model = GymLocation
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
            self.fields[f'{day}_closed'] = forms.BooleanField(
                required=False,
                widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
                label=f'{label} Closed'
            )

    def clean(self):
        cleaned_data = super().clean()
        for day, _ in self.DAYS_OF_WEEK:
            is_closed = cleaned_data.get(f'{day}_closed')
            open_time = cleaned_data.get(f'{day}_open')
            close_time = cleaned_data.get(f'{day}_close')

            if not is_closed and (not open_time or not close_time):
                raise ValidationError(f"Please specify both opening and closing times for {day.title()} or mark it as closed.")

        return cleaned_data

class SocialMediaForm(forms.Form):
    facebook = forms.URLField(required=False, widget=forms.URLInput(attrs={'class': 'form-control'}))
    instagram = forms.URLField(required=False, widget=forms.URLInput(attrs={'class': 'form-control'}))
    twitter = forms.URLField(required=False, widget=forms.URLInput(attrs={'class': 'form-control'}))
    youtube = forms.URLField(required=False, widget=forms.URLInput(attrs={'class': 'form-control'}))
    linkedin = forms.URLField(required=False, widget=forms.URLInput(attrs={'class': 'form-control'}))
