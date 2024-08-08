from django import forms
from .models import *
from django.core.exceptions import ValidationError

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

    def clean_title(self):
        title = self.cleaned_data.get('title')
        if not title:
            raise ValidationError('This field is required.')
        if len(title) < 5:
            raise ValidationError('Title must be at least 5 characters long.')
        return title

    def clean_category(self):
        category = self.cleaned_data.get('category')
        if not category:
            raise ValidationError('This field is required.')
        return category

    # def clean_post_cover(self):
    #     post_cover = self.cleaned_data.get('post_cover')
    #     if not post_cover:
    #         raise ValidationError('This field is required.')
    #     # if post_cover.size > 5 * 1024 * 1024:
    #     #     raise ValidationError('Image file too large (maximum 5mb).')
    #     return post_cover

    def clean_content(self):
        content = self.cleaned_data.get('content')
        if not content:
            raise ValidationError('This field is required.')
        if len(content) < 20:
            raise ValidationError('Content must be at least 20 characters long.')
        return content