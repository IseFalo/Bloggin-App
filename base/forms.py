from django import forms
from .models import *

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['title', 'category', 'post_cover', 'content']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'post-title my-3'}),
            'category': forms.Select(attrs={'class':'form-control my-3'}),
            'post_cover': forms.FileInput(attrs={'class':'my-3', 'id':'post-cover-input'}),
            'content': forms.Textarea(attrs={'class': 'my-3', 'placeholder':'Talk about Something...'}),
        }