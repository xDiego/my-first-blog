import datetime
from django import forms
from .models import Post, Comment, UserProfile, Blog
from django.utils.translation import ugettext_lazy as _ 
from django.contrib.auth.models import User


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ('blog', 'title', 'text',)

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('author', 'text',)

class RegisterForm(forms.Form):
    username = forms.CharField(label='username', max_length=30)
    password = forms.CharField(label='password', widget=forms.PasswordInput)
    email = forms.EmailField(label='email', widget=forms.EmailInput)

    ## Uncomment to have it work with register2 view
    # def save(self, **kwargs):
    #     newuser = User.objects.create_user(
    #         kwargs['username'],
    #         email=kwargs['email'],
    #         password=kwargs['password']
    #     )
    #     newuser.is_active = False
    #     newuser.save()
        
    #     # creating user profile 
    #     profile = UserProfile(user=newuser)
    #     profile.activation_key = kwargs['activation_key']
    #     profile.key_expires = datetime.datetime.strftime(datetime.datetime.now() + datetime.timedelta(days=2), "%Y-%m-%d %H:%M:%S")
    #     profile.save()

    #     return newuser

    # def sendEmail(self, **kwargs):

class UserSettingsForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email')

class UserProfileSettingsForm(forms.ModelForm):
    def __init__(self,qset,*args,**kwargs):
        print('qset=', qset)
        super(UserProfileSettingsForm, self).__init__(*args, **kwargs)
        if qset:
            self.fields['main_blog'] = forms.ModelChoiceField(queryset=qset, empty_label='choose a main blog')

    class Meta:
        model = UserProfile
        fields = ('main_blog',)

class BlogForm(forms.ModelForm):
    class Meta:
        model = Blog
        fields = ('name', 'description')


def formFactory(form_name):
    """Returns a form objects based on the
    given string. If form_name doesn't match
    any existing form, then None is returned.
    """
    try:
        return globals()[form_name]
    except KeyError:
        return None
