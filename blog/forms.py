from django import forms
from .models import Post    

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ('title', 'text',)

#This login form was created for testing purposes
#Delete if needed or comment out
class LoginForm(forms.Form):
    your_name = forms.CharField(label='Name', max_length=100)
    password = forms.CharField(label='Password', max_length=30)
