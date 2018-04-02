from channels.generic.websocket import WebsocketConsumer, AsyncJsonWebsocketConsumer
from asgiref.sync import async_to_sync
import json
from rest_framework import status
from chat.models import Room, Message
from channels.db import database_sync_to_async

# MSG_TYPES
MSG_LEAVE = 0
MSG_JOIN = 1
MSG_MESSAGE = 2
MSG_GREETING = 3
MSG_ALERT = 4


class ChatConsumer(WebsocketConsumer):
    def connect(self):
        self.user = self.scope['user']
        if self.user.is_anonymous:
            print('yeap')
            self.close(code=status.HTTP_401_UNAUTHORIZED)
        else:
            print(self.user)
            self.room_name = self.scope['url_route']['kwargs']['label']
            self.room_group_name = 'chat_%s' % self.room_name
            # print(self.scope)
            # Join room group
            async_to_sync(self.channel_layer.group_add)(
                self.room_group_name,
                self.channel_name
            )

            self.accept()

    def disconnect(self, close_code):
        if close_code == status.HTTP_401_UNAUTHORIZED:
            print(close_code)
            return
        try:
            async_to_sync(self.channel_layer.group_discard)(
                self.room_group_name,
                self.channel_name
            )
        except:
            print('error')

    def receive(self, text_data=None, bytes_data=None):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']

        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message
            }
        )

    def chat_message(self, event):
        message = event['message']

        # Send message to WebSocket
        self.send(text_data=json.dumps({
            'message': message
        }))


###New implementation

class MultiChatConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        if self.scope['user'].is_anonymous:
            await self.close()
        else:
            await self.accept()
        self.rooms = set()

    async def receive_json(self, content, **kwargs):
        """
        Called with decoded JSON content.
        """
        try:
            command = content.get("command", None)
            room = content["room"]

            if command == "join":
                await self.join_room(room)
            elif command == "leave":
                await  self.leave_room(room)
            elif command == "send":
                await self.message_send(content['message'], room)
        except Exception as  error:
            await self.send_json({"error": error})

    async def disconnect(self, code):
        """called when connection is lost for client for any reason"""
        try:
            for label in self.rooms:  # cpuld be exveption?
                await self.leave_room(label)
        except:
            pass  ##????

    async def message_send(self, message, label):
        if label not in self.rooms:
            raise Exception("Room access denied")
        room = await self.get_room(label)
        await self.channel_layer.group_send(
            room.group_name,
            {
                'type': 'chat.message',
                'label': label,
                'username': self.scope['user'].username,
                'message': message,
            }
        )

    async def join_room(self, label):

        room = await self.get_room(label)

        #Send other client in room that you join that room
        await self.channel_layer.group_send(
            room.group_name,
            {
                'type': 'chat.join',
                'label': label,
                'username': self.scope['user'].username
            }
        )

        # Store that we're in the room
        self.rooms.add(label)

        # Add this client to the group so he could get room messages
        await self.channel_layer.group_add(
            room.group_name,
            self.channel_name
        )
        # send client message that he successfully join this room
        await self.send_json({
            'join': room.label,
            'title': room.name
        })

    async def leave_room(self, label):
        """
        called when someone leave_room
        :param label:
        :return:
        """
        user = self.scope["user"]
        room = await self.get_room(label)

        await self.channel_layer.group_send(
            room.group_name,
            {
                'type': 'chat.leave',
                'label': label,
                'username': user.username
            }
        )
        # Remove that we're in the room
        self.rooms.discard(label)

        # Remove client from  the group so he no longer get room messages
        await self.channel_layer.group_discard(
            room.group_name,
            self.channel_name
        )

        await self.send_json({
            "leave": room.label,
        })

    async def chat_leave(self, event):
        """Called when someone leave chat"""
        await self.send_json(
            {
                'username': event['username'],
                'msg_type': MSG_LEAVE,
                'label': event['label']
            }
        )

    async def chat_join(self, event):
        """Called when someone enter a  chat"""
        await self.send_json(
            {
                'username': event['username'],
                'msg_type': MSG_JOIN,
                'label': event['label']
            }
        )

    async def chat_message(self, event):
        """Called when someone send a message"""
        await self.send_json(
            {
                'username': event['username'],
                'msg_type': MSG_MESSAGE,
                'label': event['label'],
                'message': event['message']
            }
        )



    # helpers with interaction with db

    @database_sync_to_async
    def get_room(self, label):
        try:
            room = Room.objects.get(label=label)
            return room
        except:
            print("NO Room")
            raise Exception('CREATE CUSTOM EXCEPTION')

    @database_sync_to_async
    def save_message(self, room, message):
        Message.objects.create(
            room=room,
            message=message,
            user=self.scope['user']
        )
