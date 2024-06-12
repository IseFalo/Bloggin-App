import json
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from channels.layers import get_channel_layer
from .models import *
from asgiref.sync import async_to_sync
@receiver(post_save, sender=Comment)
def send_notification_on_comment(sender, instance, created, **kwargs):
    if created:
        post = instance.post
        commenter = instance.author
        channel_layer = get_channel_layer()
        group_name= 'user-notifications'
        event = {
            'type':'user_comment',
            'text': commenter.username,
        }
        async_to_sync(channel_layer.group_send)(group_name, event)