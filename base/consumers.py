from channels.generic.websocket import WebsocketConsumer
from asgiref.sync import async_to_sync
from django.template.loader import get_template
from django.template.loader import render_to_string
import json
import re

def sanitize_username(username):
    # Replace invalid characters with underscores
    return re.sub(r'[^a-zA-Z0-9_\-\.]', '_', username)


class NotificationConsumer(WebsocketConsumer):
    def connect(self):
        self.user = self.scope['user']
        if self.user.is_authenticated:
            sanitized_username = sanitize_username(self.user.username)
            self.GROUP_NAME = f'user-notifications-{sanitized_username}'
            async_to_sync(self.channel_layer.group_add)(
                self.GROUP_NAME, self.channel_name
            )
            self.accept()
        else:
            self.close()

    def disconnect(self, close_code):
        if self.user.is_authenticated:
            async_to_sync(self.channel_layer.group_discard)(
                self.GROUP_NAME, self.channel_name
            )

    def user_comment(self, event):
        html = render_to_string("base/notification-alert.html", context={'comment_author': event['text']})
        self.send(text_data=json.dumps({
            'html': html
        }))

    def new_post(self, event):
        html = render_to_string("base/notification-alert.html", context={
            'message': event['text'],
            'post_url': event['post_url'],
            'post_cover_url': event['post_cover_url'],
        })
        self.send(text_data=json.dumps({
            'html': html
        }))