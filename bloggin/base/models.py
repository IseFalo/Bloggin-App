from django.db import models
from django.contrib.auth.models import User
# Create your models here.
class Profile(models.Model):
    username = models.OneToOneField(User, unique=True, on_delete=models.CASCADE)
    email = models.EmailField()
    profile_img=models.ImageField(upload_to="profile_images", default="blank-profile-picture.png")
    bio = models.TextField(null=True, blank=True)
    phone_no = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return self.username.username
    
class Post(models.Model):
    author= models.ForeignKey(User, on_delete=models.CASCADE)
    title=models.CharField(max_length=500)
    post_cover = models.ImageField(upload_to="post_covers")
    content=models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    read = models.ManyToManyField(User, related_name="blog_posts")
    edited = models.BooleanField(default=False) 

    def __str__(self):
        return self.title
    
class Comment(models.Model):
    post=models.ForeignKey(Post, on_delete=models.CASCADE)
    author=models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Comment by {self.author.username} on {self.post.title}"