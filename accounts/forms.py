from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, PasswordChangeForm
from django.contrib.auth import get_user_model, authenticate
from django.utils.translation import gettext_lazy as _

User = get_user_model()

class CustomUserCreationForm(UserCreationForm):
    first_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    last_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    studio_name = forms.CharField(
        max_length=255,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'class': 'form-control'}))

    class Meta:
        model = User
        fields = ('email', 'first_name', 'last_name', 'studio_name', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs['class'] = 'form-control'
        self.fields['password2'].widget.attrs['class'] = 'form-control'

    def save(self, commit=True):
        user = super().save(commit=False)
        user.user_type = 'owner'
        if commit:
            user.save()
        return user

    def clean(self):
        cleaned_data = super().clean()
        studio_name = cleaned_data.get('studio_name')
        
        if not studio_name:
            self.add_error('studio_name', 'Studio name is required for studio owners')
        
        return cleaned_data

class CustomAuthenticationForm(AuthenticationForm):
    username = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))

    error_messages = {
        'invalid_login': _(
            "Please enter a correct email and password. Note that both "
            "fields may be case-sensitive."
        ),
        'inactive': _("This account is inactive."),
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].label = 'Email'

    def clean(self):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')

        if username and password:
            self.user_cache = authenticate(
                self.request, username=username, password=password
            )
            if self.user_cache is None:
                raise forms.ValidationError(
                    self.error_messages['invalid_login'],
                    code='invalid_login',
                )
            else:
                self.confirm_login_allowed(self.user_cache)

        return self.cleaned_data

class CustomPasswordChangeForm(PasswordChangeForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['old_password'].widget.attrs['class'] = 'form-control'
        self.fields['new_password1'].widget.attrs['class'] = 'form-control'
        self.fields['new_password2'].widget.attrs['class'] = 'form-control'

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
        for day, day_name in self.DAYS_OF_WEEK:
            self.fields[f'{day}_closed'] = forms.BooleanField(required=False, label=f'{day_name} Closed')
            self.fields[f'{day}_open'] = forms.TimeField(
                required=False,
                widget=forms.TimeInput(attrs={'type': 'time'}),
                label=f'{day_name} Opening Time'
            )
            self.fields[f'{day}_close'] = forms.TimeField(
                required=False,
                widget=forms.TimeInput(attrs={'type': 'time'}),
                label=f'{day_name} Closing Time'
            )

    def clean(self):
        cleaned_data = super().clean()
        for day, _ in self.DAYS_OF_WEEK:
            is_closed = cleaned_data.get(f'{day}_closed')
            open_time = cleaned_data.get(f'{day}_open')
            close_time = cleaned_data.get(f'{day}_close')

            if not is_closed and (not open_time or not close_time):
                raise forms.ValidationError(f'Please specify both opening and closing times for {day} or mark it as closed.')
            
            if open_time and close_time and open_time >= close_time:
                raise forms.ValidationError(f'Opening time must be before closing time for {day}.')

        return cleaned_data
