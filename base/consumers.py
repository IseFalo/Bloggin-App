from channels.generic.websocket import WebsocketConsumer
from asgiref.sync import async_to_sync
from django.template.loader import get_template
from django.template.loader import render_to_string
import json



class NotificationConsumer(WebsocketConsumer):
    def connect(self):
        self.GROUP_NAME = 'user-notifications'
        async_to_sync(self.channel_layer.group_add)(
            self.GROUP_NAME, self.channel_name
        )
        self.accept()

    def disconnect(self, close_code):
        # Leave room group
        async_to_sync(self.channel_layer.group_discard)(
            self.GROUP_NAME, self.channel_name
        )

    def user_comment(self, event):
        html = render_to_string("base/notification-alert.html", context={'comment_author': event['text']})
        self.send(text_data=json.dumps({
            'html': html
        }))