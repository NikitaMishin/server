from channels.generic.websocket import WebsocketConsumer, AsyncJsonWebsocketConsumer
from asgiref.sync import async_to_sync
import json
from rest_framework import status
from chat.models import Room, Message
from channels.db import database_sync_to_async
from django.contrib.auth.models import User

# MSG_TYPES
MSG_LEAVE = 0
MSG_JOIN = 1
MSG_MESSAGE = 2
MSG_GREETING = 3
MSG_ALERT = 4

###New implementation AsyncJson\

### in handshake we validate  user token
### then on receive_json  we   check  what commands and  and check access to room and
###rooms self.scope['user']??

"""
    Description:
    
    
    available commands:
    join: join room
    //
      Notificate other users in room that you joined
      Notificate user that successful join with greeting message
      Get all previous messages if exists 
    //
    
    leave: leave room
    //
        Notificate other users that you leave room (go offline)
        Send user that he succesfully left room
    //
    
    send: send message in room
    //
        Send message to specific room
        Notificate other users that
        user send a message
    
    //
    
    notificate user:
        ????
    //
    
    //
    notificate user:
        ????
    //
    
    //
    
    complete_challenge:
    
    //
    ?
    
    //
    
    approve_challenge:
    //

    //
    
    reconnect: reconnect user to active rooms where he play
    //
        ?
    //
    
"""


class MultiChatConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        self.user = self.scope['user']
        if self.user.is_anonymous:
            await self.close()
        else:
            await self.accept()
        self.rooms = set()

    async def receive_json(self, content, **kwargs):
        """
        Called with decoded JSON content.
        if reconnect then return last n messages
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
            elif command == "quit":
                pass
            elif command == "ready":
                pass
            elif command == "complete_challenge":
                pass
            elif command == "approve_challenge":
                pass
            elif command == "notificate_user":
                pass
            elif command == "notificate_users":
                pass
            elif command == "reconnect":
                pass




        except Exception as  error:
            await self.send_json({"error": 'error'})

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

        # Send other client in room that you join that room
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

    async def chats_reconnection(self):
        user = self.scope['user']
        channelsnames = map('', user.rooms.label)
        self.channel_layer.group_send()  # send other that u reconnect
        self.rooms.add(rooms)
        self.channel_layer.group.add()  ##add us two our rooms
        self.send_json({  # send last 50 messages in each room for clien
            'reconnected': True,
            'room': {}
        })

    # fetch last 50 messages
    async def chat_refresh(self):
        pass

    # helpers with interaction with db

    # tipa ok
    @database_sync_to_async
    def get_room(self, label):
        """
        Get room from by label from rooms,update room.users if needed and return room
        :raise Access denied
        :param label:
        :return: room
        """

        try:
            room = Room.objects.get(label=label)
        except Exception:  # doesnot exits
            raise Exception("RoomDoesnotExist")

        user = User(self.user).userprofile
        if room.size < room.users.count() and user not in room.users:
            # register user to this room and return room
            room.users.add(user)
            return room
        elif user in room.users:
            return room
        else:
            # room alreay full
            raise Exception('Access Denied')

    # ok
    @database_sync_to_async
    def save_message(self, room, message):
        Message.objects.create(
            room=room,
            message=message,
            user=self.user.profile
        )

    @database_sync_to_async
    def get_user_rooms(self, user):
        room = user.openrooms
        return room

    @database_sync_to_async
    def remove_from_room(self, room):
        pass
