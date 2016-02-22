import hashlib
import random
import itertools
from django.shortcuts import render
from django.utils import timezone
from django.shortcuts import redirect, get_object_or_404
from .models import Post, Comment, UserProfile, Blog
from .forms import PostForm, CommentForm, RegisterForm, UserSettingsForm, BlogForm
from .signals import update_num_post
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate
from django import forms
from django.dispatch import Signal

## Cache
blog_nav_cache = None


# Create your views here.
def main_page(request):
    return render(request, 'blog/index.html')

@login_required
def settings_page(request):
    # check if user is authenticated
    if request.user.is_authenticated() and request.method == "GET":
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

        ## blog settings
        blog_list = Blog.objects.filter(owner__user=request.user)
        
        return render(request, 'blog/user_settings.html', {'form':form, 'blog_list':blog_list})

    elif request.method == "POST": #POST method
        form = UserSettingsForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()  #update user profile
 
            return render(request, 'blog/user_settings.html', {'form':form}) 

    return redirect('django.contrib.auth.views.login')

@login_required
def user_profile_settings(request):
    # profile = UserProfile.objects.get(user=request.user)
    # form = UserProfileSettingsForm(
    #     initial={
    #         'name':request.user.username,
    #         'num_blogs':profile.num_blogs
    #     }
    # )
    # return render(request, 'blog/user_profile_settings.html', {'form':form})
    pass

@login_required
def blog_settings(request):
    """Choose a blog and change it's settings
    E.G:
        - Change blog name
        - Description
        - Manage Posts/Comments
        - ....
    """
    blog_list = Blog.objects.filter(owner__user=request.user)
    return render(request, 'blog/blog_settings.html', {'blogs':blog_list})

@login_required
def blog_edit(request, pk):
    blog = get_object_or_404(Blog, pk=pk)
    if request.method == "POST":
        form = BlogForm(request.POST, instance=blog)
        if form.is_valid():
            b = form.save()
            return redirect('blog_settings')
    else:
        form = BlogForm()

    return render(request, 'blog/blog_edit.html', {'form': form, 'blog':blog})

def follow(request, pk):
    """Follow a person
    """
    pass

def follower_suggestion(user):
    """Show suggestion for this user to follow
    based on people you follow(e.g: people you follow that
    may have same interest on you. Or purely based on users followed
    by someone you follow.)
    """
    pass

def dashboard(request):
    """The main dashboard that shows the post from users
    that user follows.    
    """
    ## Get follower posts
    ## Limit number of posts by 50 posts
    
    ## Way 1
    ## - get all followers from user
    ## - get posts from each one
    followers = request.user.profile.follows.all()
    posts_list = [follower.user.post_set.all() for follower in followers]
    all_posts = list(itertools.chain(*posts_list))
    sorted_posts = sorted(all_posts, key=lambda x: x.published_date, reverse=True)

    return render(request, 'blog/dashboard.html', {'post_list':sorted_posts})

def post_list1(request, pk):
    """Queries the DB for all the posts that match PK
    TODO: make sure it belongs to request.user????

    TODO: check if the blog belongs to request.user, if so then show
    the side control panel, otherwise don't.

    """
    global blog_nav_cache
    posts = Post.objects.filter(blog__pk=pk).order_by('-published_date')
    blogs = Blog.objects.filter(owner__user=request.user)
    return render(request, 'blog/post_list.html', {'posts':posts, 'pk':pk, 'blogs':blogs})

def post_list(request):
    """Queries the DB for all the posts that match request.user
    """
    ## TODO:
    ## Figure out how to print Posts for the Blog selected
    ## and not all the Post from every blog

    ## query db for users post only
    posts = Post.objects.filter(author=request.user).order_by('-published_date')
    blogs = Blog.objects.filter(owner__user=request.user)
    return render(request, 'blog/post_list.html', {'posts':posts, 'blogs':blogs})

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
    
    if post.blog:
        update_num_post.send(sender=None, blog=post.blog)

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
    """Handles the creation of a blog
    """

    if request.method == "POST":
        form = BlogForm(request.POST)
        
        if form.is_valid():
            new_blog = Blog.objects.create(
                owner=request.user.profile,
                name=form.cleaned_data.get('name'),
                description=form.cleaned_data.get('description')
            )
            new_blog.save()

            return redirect('blog.views.blog_settings')
    else:
        form = BlogForm()

    blogs = Blog.objects.filter(owner__user=request.user)
    return render(request, 'blog/create_blog.html', {'form':form, 'blogs':blogs})
