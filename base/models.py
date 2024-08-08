from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.utils import timezone
from django.db.models import Count
from ckeditor.fields import RichTextField
from ckeditor_uploader.fields import RichTextUploadingField

import uuid
import readtime
# Create your models here.
class Profile(models.Model):
    username = models.OneToOneField(User, unique=True, on_delete=models.CASCADE)
    email = models.EmailField()
    profile_img=models.ImageField(upload_to="profile_images", default="blank-profile-picture.png")
    bio = models.TextField(null=True, blank=True)
    phone_no = models.IntegerField(null=True, blank=True)
    top_picks = models.ManyToManyField('Post', blank=True)
    followers = models.ManyToManyField(User, related_name="following")
    saved_posts = models.ManyToManyField('Post', related_name="saved_by")

    def __str__(self):
        return self.username.username

class Category(models.Model):
    name = models.CharField(max_length=150)
    def __str__(self):
        return self.name
class Series(models.Model):
    creator=models.ForeignKey(User, on_delete=models.CASCADE)
    name=models.CharField(max_length=200)
    series_cover = models.ImageField(upload_to="series_covers" , default="series-default.png")
    description = models.TextField(null=True)
    organization = models.ForeignKey('Organization', null=True, on_delete=models.SET_NULL)
    def __str__(self):
        return self.name
class Post(models.Model):
    author= models.ForeignKey(User, on_delete=models.CASCADE)
    title=models.CharField(max_length=500)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, null=True)
    post_cover = models.ImageField(upload_to="post_covers", default="no-image.png")
    content= RichTextUploadingField()
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    read = models.ManyToManyField(User, related_name="blog_posts")
    likes = models.ManyToManyField(User, related_name="likedposts")
    edited = models.BooleanField(default=False)
    is_top_pick = models.BooleanField(default=False)
    series = models.ForeignKey(Series, null=True, on_delete=models.SET_NULL)
    top_pick_selected_at = models.DateTimeField(null=True, blank=True)
    STATUS_CHOICES = (
        ('draft', 'Draft'),
        ('published', 'Published'),
    )
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='draft')
    organization = models.ForeignKey('Organization', null=True ,on_delete=models.SET_NULL)
    def __str__(self):
        return self.title
    
    def get_read_time_in_seconds(self):
        """
        Calculates the estimated reading time for the post's content.
        """
        word_count = len(self.content.split())
        read_time_in_seconds = word_count*0.5
        return round(read_time_in_seconds)
    
    

    def get_read_time_in_minutes(self):
        word_count = len(self.content.split())
        read_time_in_seconds = word_count*0.5
        read_time_in_minutes = read_time_in_seconds/60
        if read_time_in_minutes < 1:
            # read_time_in_minutes = 1
            return('<1')
        return round(read_time_in_minutes)

    @property
    def like_count(self):
        return self.likes.all().count()
    @property
    def read_count(self):
        return self.read.all().count()

class LikedPost(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f'{self.user.username} : {self.post.title}'

@receiver(pre_save, sender=Post)
def update_top_pick_timestamp(sender, instance, **kwargs):
    if instance.is_top_pick and instance._state.adding:  # Only update timestamp on creation
        instance.top_pick_selected_at = timezone.now()
        Notification.objects.create(user=instance.author, post=instance, message="Your post was marked as top pick")

class Comment(models.Model):
    post=models.ForeignKey(Post, on_delete=models.CASCADE)
    author=models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    id = models.CharField(max_length=100, default=uuid.uuid4, unique=True, primary_key = True, editable=False)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Comment by {self.author.username} on {self.post.title}"

    def save(self, *args, **kwargs):
        is_new_comment = self.pk is None  # Check if it's a new comment
        super().save(*args, **kwargs)

        if is_new_comment:
            Notification.objects.create(user=self.post.author, comment=self, post=self.post, message=" Commented on your Post")


class Reply(models.Model):
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="replies")
    parent_comment = models.ForeignKey(Comment, on_delete=models.CASCADE, related_name="replies")
    body = models.CharField(max_length=150)
    created = models.DateTimeField(auto_now_add=True)
    id = models.CharField(max_length=100, default=uuid.uuid4, unique=True, primary_key = True, editable=False)

    def __str__(self):
        try:
            return f'{self.author.username} : {self.body[:30]}'
        except:
            return f'no author : {self.body[:30]}'

    class Meta:
        ordering = ['created']




class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, null=True, blank=True)
    post_url = models.URLField(max_length=200, null=True, blank=True)
    post_cover_url = models.URLField(max_length=200, null=True, blank=True)
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, null=True, blank=True)
    message = models.CharField(max_length=500, null=True, blank=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Notification | {self.user.username}"
    
class Organization(models.Model):
    creator = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    name=models.CharField(max_length=200, unique=True)
    profile_img=models.ImageField(upload_to="profile_images", default="blank-org-profile.jpg")
    bio=models.TextField()
    top_picks = models.ManyToManyField('Post', blank=True, related_name='featured_in_organizations')
    followers = models.ManyToManyField(User, related_name="followings")
    members = models.ManyToManyField(User, related_name="organizations")

    def __str__(self):
        return self.name