from django import forms
from .models import Post, Comment, UserProfile
from django.utils.translation import ugettext_lazy as _ 
from django.contrib.auth.models import User

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ('title', 'text',)

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('author', 'text',)

class RegisterForm(forms.Form):
    username = forms.CharField(label='username', max_length=30)
    password = forms.CharField(label='password', widget=forms.PasswordInput)
    email = forms.EmailField(label='email', widget=forms.EmailInput)
