from django import forms
from .models import Video, Comment, Category, Playlist, PlaylistVideo

class VideoUploadForm(forms.ModelForm):
    category = forms.ModelChoiceField(
        queryset=Category.objects.none(),
        empty_label="Select a category",
        widget=forms.Select(attrs={
            'class': 'block w-full sm:text-sm border-gray-300 rounded-lg focus:ring-indigo-500 focus:border-indigo-500 transition duration-150 ease-in-out'
        })
    )

    class Meta:
        model = Video
        fields = ['title', 'description', 'file', 'category']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'block w-full sm:text-sm border-gray-300 rounded-md',
                'placeholder': 'Video title'
            }),
            'description': forms.Textarea(attrs={
                'rows': 3,
                'class': 'block w-full sm:text-sm border-gray-300 rounded-md',
                'placeholder': 'Video description'
            })
        }

    def __init__(self, *args, **kwargs):
        studio = kwargs.pop('studio', None)
        super().__init__(*args, **kwargs)
        if studio:
            self.fields['category'].queryset = Category.objects.filter(studio=studio)

    def clean_file(self):
        file = self.cleaned_data.get('file')
        if file:
            if file.size > 1024 * 1024 * 500:  # 500MB limit
                raise forms.ValidationError('File size must be under 500MB')
            return file
        return None

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={
                'rows': 3,
                'class': 'block w-full pr-3 py-2 pl-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm transition-shadow duration-200',
                'placeholder': 'Share your thoughts...'
            })
        }

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'description']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'block w-full sm:text-sm border-gray-300 rounded-md',
                'placeholder': 'Category name'
            }),
            'description': forms.Textarea(attrs={
                'rows': 3,
                'class': 'block w-full sm:text-sm border-gray-300 rounded-md',
                'placeholder': 'Category description'
            })
        }

class PlaylistForm(forms.ModelForm):
    class Meta:
        model = Playlist
        fields = ['name', 'description', 'is_public']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'block w-full sm:text-sm border-gray-300 rounded-md',
                'placeholder': 'Playlist name'
            }),
            'description': forms.Textarea(attrs={
                'rows': 3,
                'class': 'block w-full sm:text-sm border-gray-300 rounded-md',
                'placeholder': 'Playlist description'
            })
        }

class PlaylistVideoForm(forms.ModelForm):
    class Meta:
        model = PlaylistVideo
        fields = ['video', 'order']
