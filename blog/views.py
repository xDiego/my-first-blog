import hashlib
import random
from django.shortcuts import render
from django.utils import timezone
from django.shortcuts import redirect, get_object_or_404
from .models import Post, Comment, UserProfile, Blog
from .forms import PostForm, CommentForm, RegisterForm, UserSettingsForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate
from django import forms

# Create your views here.
def main_page(request):
    return render(request, 'blog/index.html')

@login_required
def settings_page(request):
    # check if user is authenticated
    if request.user.is_authenticated() and request.method == "GET":
        print('user authenticated')
        # Query DB for UserProfile settings
#        user = User.objects.filter(username=request.user)[0]
        user = request.user  ## this is a replacement for the above code
                             ## don't have to fetch user from DB
        form = UserSettingsForm(
            initial={
                'first_name':user.first_name,
                'last_name':user.last_name,
                'email':user.email,
                'last_login':user.last_login,
                'date_joined':user.date_joined
            }
        )
        return render(request, 'blog/user_settings.html', {'form':form})

    elif request.method == "POST": #POST method
        form = UserSettingsForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()  #update user profile
 
            return render(request, 'blog/user_settings.html', {'form':form}) 

    return redirect('django.contrib.auth.views.login')

def post_list1(request, pk):
#    posts = Post.objects.filter(blog__pk=pk, author=request.user).order_by('-published_date')
    posts = Post.objects.filter(blog__pk=pk).order_by('-published_date')
    print('post_list1')
    print(posts)
    return render(request, 'blog/post_list.html', {'posts':posts})

def post_list(request):
    ## TODO:
    ## Figure out how to print Posts for the Blog selected
    ## and not all the Post from every blog

    ## query db for users post only
    posts = Post.objects.filter(author=request.user).order_by('-published_date')

    return render(request, 'blog/post_list.html', {'posts':posts})

def post_detail(request, pk):
    post = get_object_or_404(Post, pk=pk)
    return render(request, 'blog/post_detail.html', {'post': post})

@login_required
def post_new(request):

    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect('post_detail', pk=post.pk)
    else:
        # Limit the Blog options to users blog
        q_set = Blog.objects.filter(owner__user = request.user)
        PostForm.base_fields['blog'] = forms.ModelChoiceField(queryset=q_set, empty_label='Choose a Blog')
        form = PostForm()
            
    return render(request, 'blog/post_edit.html', {'form': form})

@login_required
def post_edit(request, pk):

    post = get_object_or_404(Post, pk=pk)

    if request.method == 'POST':
        form = PostForm(request.POST, instance=post)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.published_date = timezone.now()
            post.save()
            return redirect('post_detail', pk=post.pk)
    else:
        form = PostForm(instance=post)
            
    return render(request, 'blog/post_edit.html', {'form': form})

@login_required
def post_draft_list(request):
    """Will post drafted posts
    """
    posts = Post.objects.filter(published_date__isnull=True).order_by('created_date')
    return render(request, 'blog/post_draft_list.html', {'posts':posts})

@login_required
def post_publish(request, pk):
    """View to publish drafted posts
    """
    post = get_object_or_404(Post, pk=pk)
    post.publish()
    return redirect('blog.views.post_detail', pk=pk)

@login_required
def post_remove(request, pk):
    """Remove a post
    """
    post = get_object_or_404(Post, pk=pk)
    post.delete()
    return redirect('blog.views.post_list')

def register(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            ## TODO:
            ## 1) Redirect to profile settings
            ## 2) Do Email Authentication that way We don't let
            ## users do much without authentication. Otherwise
            ## bots could just flood the system.
            ## 3) After user creation, log them in automatically.
            name, password = form.cleaned_data.get('username'), form.cleaned_data.get('password')
            newuser = User.objects.create_user(name, password=password)
            newuser.email = form.cleaned_data.get('email')
            newuser.save()

            uname = request.POST['username']
            pw = request.POST['password']
            uu = authenticate(username=uname, password=pw)
            
            if uu:
                if uu.is_active:
                    login(request, uu)
                    redirect('blog.views.post_list')
            

            return redirect('blog.views.post_list')
    else:
        # check if person is authenticated, if so redirect them to 
        # Post_List
        if request.user.is_authenticated():
            return redirect('blog.views.post_list')
        else:
            form = RegisterForm()
    return render(request, 'blog/register.html', {'form':form})

def register2(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            ## TODO:
            ## 1) Redirect to profile settings
            ## 2) Do Email Authentication that way We don't let
            ## users do much without authentication. Otherwise
            ## bots could just flood the system.
            ## 3) After user creation, log them in automatically.
            kwargs = {}
            kwargs['username'] = form.cleaned_data.get('username')
            kwargs['password'] = form.cleaned_data.get('password')
            kwargs['email']    = form.cleaned_date.get('email')
            
            # creating authentication key
            salt = hashlib.sha1(str(random.random())).hexdigest()[:5]
            if isinstance(kwargs['email'], unicode):
                email = email.encode('utf-8')
            kwargs['activation_key'] = hashlib.sha1(salt+email).hexdigest()
            kwargs['email_subject'] = "Authenticate you account"
            

            form.sendEmail(kwargs)
            form.save(kwargs)

            return redirect('blog.views.post_list')
    else:
        # check if person is authenticated, if so redirect them to 
        # Post_List
        if request.user.is_authenticated():
            return redirect('blog.views.post_list')
        else:
            form = RegisterForm()
    return render(request, 'blog/register.html', {'form':form})

@login_required
def add_comment_to_post(request, pk):
    """Enable Users to add comments to the post
    """
    post = get_object_or_404(Post, pk=pk)
    if request.method == "POST":
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post 
            comment.save()
            return redirect('blog.views.post_detail', pk=post.pk)
    else:
        form = CommentForm()
    print('GET')
    return render(request, 'blog/add_comment_to_post.html',{'form':form})

## TODO
## - Edit the comment_approve/remove so that only the owner
##   of the blog can approve or remove.
@login_required
def comment_approve(request, pk):
    comment = get_object_or_404(Comment, pk=pk)
    comment.approve()
    return redirect('blog.views.post_detail', pk=comment.post.pk)


@login_required
def comment_remove(request, pk):
    comment = get_object_or_404(Comment, pk=pk)
    post_pk = comment.post.pk
    comment.delete()
    return redirect('blog.views.post_detail', pk=post_pk)

@login_required
def create_blog(request):
    pass
