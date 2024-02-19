from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.utils import timezone
from django.db.models import Count
import uuid
# Create your models here.
class Profile(models.Model):
    username = models.OneToOneField(User, unique=True, on_delete=models.CASCADE)
    email = models.EmailField()
    profile_img=models.ImageField(upload_to="profile_images", default="blank-profile-picture.png")
    bio = models.TextField(null=True, blank=True)
    phone_no = models.IntegerField(null=True, blank=True)
    top_picks = models.ManyToManyField('Post', blank=True)
    followers = models.ManyToManyField(User, related_name="following")

    def __str__(self):
        return self.username.username

class Category(models.Model):
    name = models.CharField(max_length=150)
    def __str__(self):
        return self.name
class Post(models.Model):
    author= models.ForeignKey(User, on_delete=models.CASCADE)
    title=models.CharField(max_length=500)
    # category = models.ForeignKey(Category, on_delete=models.CASCADE)
    post_cover = models.ImageField(upload_to="post_covers")
    content=models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    read = models.ManyToManyField(User, related_name="blog_posts")
    likes = models.ManyToManyField(User, related_name="likedposts", through="LikedPost")
    edited = models.BooleanField(default=False)
    is_top_pick = models.BooleanField(default=False)
    top_pick_selected_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.title

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
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, null=True, blank=True)
    message = models.CharField(max_length=500, null=True, blank=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Notification | {self.user.username}"
