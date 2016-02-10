from django.db import models
from django.utils import timezone
from django.conf import settings
from django.contrib.auth.models import User
from django.dispatch import receiver
from django.db.models.signals import post_save
from .signals import update_num_post

# Create your models here.
class UserProfile(models.Model):
    # Relationships
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        related_name="profile"
    )

    # Attributes - Mandatory
    num_blogs = models.IntegerField(default=0)
    activation_key = models.CharField(max_length=40, default="empty")
    key_expires = models.DateTimeField(null=True)    

    # Custom Property
    def username(self):
        return self.user.username

    # Methods

    def __str__(self):
        return self.user.username

#signaling
@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_profile_for_new_user(sender, created, instance, **kwargs):
    if created:
        profile = UserProfile(user=instance)
        profile.save()

class Blog(models.Model):
    owner = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    description = models.CharField(max_length=200)
    num_posts = models.IntegerField(default=0)

    def __str__(self):
        return self.name
    
class Post(models.Model):
    author = models.ForeignKey('auth.User')
    blog = models.ForeignKey(Blog, on_delete=models.CASCADE, null=True)
    title = models.CharField(max_length=200)
    text = models.TextField()
    created_date = models.DateTimeField(
        default=timezone.now)
    published_date = models.DateTimeField(
        blank=True, null=True)

    def publish(self):
        self.published_date = timezone.now()
        self.save()
        self.blog.num_posts += 1
        self.blog.save()

    def approved_comments(self):
        return self.comments.filter(approved_comment=True)

    def __str__(self):
        return self.title

class Comment(models.Model):
    # Relationship
    post = models.ForeignKey('blog.Post', related_name='comments')

    # Attributes
    author = models.CharField(max_length=200)
    text = models.TextField()
    created_date = models.DateField(default=timezone.now)
    approved_comment = models.BooleanField(default=False)

    # Method
    def approve(self):
        """approve the comment
        """
        self.approved_comment = True
        self.save()

    def __str__(self):
        return self.text

def handle_update_num_post(sender, **kwargs):
    if kwargs:
        blog = kwargs['blog']
        blog.num_posts = blog.num_posts - 1
        if blog.num_posts < 0:
            blog.num_posts = 0
        blog.save()

update_num_post.connect(handle_update_num_post)
