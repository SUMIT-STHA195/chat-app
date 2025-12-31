# import json

# from channels.generic.websocket import WebsocketConsumer

# class ChatConsumer(WebsocketConsumer):
#     def connect(self):
#         self.accept()

#     def disconnect(self, close_code):
#         pass

#     def receive(self, text_data):
#         text_data_json=json.loads(text_data)
#         message=text_data_json["message"]
#         self.send(text_data=json.dumps({'message':message}))

import json
from channels.generic.websocket import AsyncWebsocketConsumer
from .models import Message, Room
from django.contrib.auth.models import User
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
        message=await self.save_message(message, room_name, user)
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "chat_message",
                "message":message
                
            }
        )

    async def chat_message(self, event):
        context=event['message']
        # print(context.sender.username)
        # print("CHAT MESSAGE CALLED:", message)
        # print(user)
        # print(user)
        await self.send(text_data=json.dumps({"sender": context.sender.username,
                "content": context.content,
                "timestamp":context.timestamp.astimezone(ZoneInfo('Asia/Kathmandu')).strftime("%H:%M")}))

    @database_sync_to_async
    def save_message(self, message, room_name, user):
        room = Room.objects.get(room_name=room_name)
        user = User.objects.get(username=user)
        message = Message.objects.create(
            content=message,
            room=room,
            sender=user
        )
        message.save()
        return message
    