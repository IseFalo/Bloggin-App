import json
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from channels.layers import get_channel_layer
from .models import *
from asgiref.sync import async_to_sync
import re
from django.urls import reverse

def sanitize_username(username):
    # Replace invalid characters with underscores
    return re.sub(r'[^a-zA-Z0-9_\-\.]', '_', username)




@receiver(post_save, sender=Comment)
def send_notification_on_comment(sender, instance, created, **kwargs):
    if created:
        post = instance.post
        post_author = post.author  # Assuming 'owner' is the field in the Post model
        commenter = instance.author
        post_url = reverse('post-detail', kwargs={'pk': post.pk}) 
        post_cover_url = post.post_cover.url if post.post_cover else 'default_image_url'
        message = f'New comment on your post by {instance.author.username}'
        Notification.objects.create(user=post_author, message=message, post_url=post_url, post_cover_url=post_cover_url)
        channel_layer = get_channel_layer()
        sanitized_username = sanitize_username(post_author.username)
        group_name = f'user-notifications-{sanitized_username}'
        event = {
            'type': 'user_comment',
            'text': commenter.username,
            'post_url': post_url,
            'post_cover_url': post_cover_url,
        }
        async_to_sync(channel_layer.group_send)(group_name, event)


@receiver(post_save, sender=Post)
def send_notification_on_new_post(sender, instance, created, **kwargs):
    if created:
        post = instance
        post_author = post.author
        post_url = reverse('post-detail', kwargs={'pk': post.pk})
        post_cover_url = post.post_cover.url if post.post_cover else 'default_image_url'
        message = f'{post_author.username} has created a new post: {post.title}'

        profile = Profile.objects.get(username=post_author)
        followers = profile.followers.all()

        for follower in followers:
            Notification.objects.create(user=follower, message=message, post_url=post_url, post_cover_url=post_cover_url)
            channel_layer = get_channel_layer()
            sanitized_username = sanitize_username(follower.username)
            group_name = f'user-notifications-{sanitized_username}'
            event = {
                'type': 'new_post',
                'text': message,
                'post_url': post_url,
                'post_cover_url': post_cover_url,
            }
            async_to_sync(channel_layer.group_send)(group_name, event)
