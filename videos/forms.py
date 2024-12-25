from django import forms
from .models import Video

class VideoUploadForm(forms.ModelForm):
    class Meta:
        model = Video
        fields = ['title', 'description', 'file']
        
    def clean_file(self):
        file = self.cleaned_data.get('file')
        if file:
            if file.size > 1024 * 1024 * 500:  # 500MB limit
                raise forms.ValidationError('File size must be under 500MB')
            return file
        return None
