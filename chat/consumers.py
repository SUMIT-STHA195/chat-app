import json
from channels.generic.websocket import AsyncWebsocketConsumer
from .models import Message, Room, Notification
# from django.contrib.auth.models import User
from authentication.models import CustomUser
from channels.db import database_sync_to_async
from zoneinfo import ZoneInfo


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
        # print(self.room_name)
        self.room_group_name = f"chat_{self.room_name}"
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()
        await self.mark_as_read()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name, self.channel_name
        )

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json["message"]
        user = self.scope['user'].username
        print(user)
        room_name = self.room_name
        message = await self.save_message(message, room_name, user)
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "chat_message",
                "message": message

            }
        )

    async def chat_message(self, event):
        context = event['message']
        await self.send(text_data=json.dumps({"sender": context.sender.username,
                                              "content": context.content,
                                              "timestamp": context.timestamp.astimezone(ZoneInfo('Asia/Kathmandu')).strftime("%H:%M")}))

    @database_sync_to_async
    def save_message(self, message, room_name, user):
        room = Room.objects.get(room_name=room_name)
        user = CustomUser.objects.get(username=user)
        message = Message.objects.create(
            content=message,
            room=room,
            sender=user
        )
        message.save()
        return message

    @database_sync_to_async
    def mark_as_read(self):
        room = Room.objects.get(room_name=self.room_name)
        Notification.objects.filter(
            recipient_id=self.scope['user'].id,
            message__room_id=room.id,
            is_read=False,
        ).update(is_read=True)


class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope["user"]
        if self.user.is_authenticated:
            self.group_name = f'notify_{self.user.id}'
            await self.channel_layer.group_add(
                self.group_name,
                self.channel_name
            )
            await self.accept()
            notification_context = await self.get_notification()
            await self.send(text_data=json.dumps({
                "type": "initial_notification",
                "notification_context": notification_context,
            }))
        else:
            await self.close()

    async def disconnect(self, code):
        if self.scope['user'].is_authenticated:
            await self.channel_layer.group_discard(
                self.group_name,
                self.channel_name
            )

    async def receive(self, text_data):
        data = json.loads(text_data)
        if data.get('action') == 'mark_read':
            await self.mark_all_as_read()

    @database_sync_to_async
    def mark_all_as_read(self):
        Notification.objects.filter(
            recipient=self.user, is_read=False).update(is_read=True)

    async def send_notification(self, event):
        await self.send(text_data=json.dumps({
            'type': 'send_notification',
            'notification_context': event['notification_context'],
        }))

    @database_sync_to_async
    def get_notification(self):
        # notification = Notification.objects.filter(recipient_id=self.user.id)
        notifications = Notification.objects.filter(
            recipient=self.user,
            is_read=False
        ).select_related('message__sender', 'message__room')
        notification_context = [
            {
                "message": f"New message from {x.message.sender.first_name}",
                "sender_username": x.message.sender.username,
                "is_group": x.message.room.is_group,
                "group_name": x.message.room.room_name,
                "is_read": x.is_read,
            }
            for x in notifications
        ]
        return notification_context
