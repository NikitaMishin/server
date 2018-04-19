from channels.generic.websocket import WebsocketConsumer, AsyncJsonWebsocketConsumer
from asgiref.sync import async_to_sync
import json
from rest_framework import status

from chat.game_logic.models import Game, prepare_game, vote, get_next_challenge, COMPLETED
from chat.models import Room, Message, UserProfile
from channels.db import database_sync_to_async
from django.contrib.auth.models import User

# MSG_TYPES
from chat.serializers import MessageSerializers
from database.models import Challenge

MSG_LEAVE = 0
MSG_JOIN = 1
MSG_MESSAGE = 2
MSG_GREETING = 3
MSG_ALERT = 4

ACTION_QUIT = 'quit'
ACTION_NEXT_CHALLENGE = 'next challenge'
ACTION_APPROVE = 'approve'
ACTION_WENT_OFFLINE = 'went offline'
ACTION_JOIN = 'join'
ACTION_RECONNECT = 'reconnect'
ACTION_MESSAGE = 'message'
ACTION_REFRESH_CHAT = 'refresh_chat'
ACTION_COMPLETE = 'complete'
ACTION_ERROR = 'error'
ACTION_USER_COMPLETE = 'user complete'
ACTION_DENIED = 'denied'
ACTION_ONLINE = 'online'
###New implementation AsyncJson\

### in handshake we validate  user token
### then on receive_json  we   check  what commands and  and check access to room and
###rooms self.scope['user']??

"""
    Description:
    Когда кто-то выполнил челлендж,
    
    available commands:
    join: join room
    //
      Notificate other users in room that you joined
      Notificate user that he successfully join with greeting message
      Get all previous messages if exists 
    //
    
    leave: leave room
    //
        Notificate other users that you leave room (go offline)
        Send user that he successfully left room
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
            self.userprofile = self.user.userprofile
            await self.accept()
        self.rooms = set()

    async def receive_json(self, content, **kwargs):
        """

        """
        try:
            command = content.get("command", None)
            room_label = content["room_label"]

            if command == "join":
                await self.join_room(room_label)
            elif command == "leave":
                await  self.leave_room(room_label)
            elif command == "send":
                await self.message_send(content['message'], room_label)
            elif command == "quit":
                await self.quit_room(room_label)
            elif command == "complete_challenge":
                await self.complete_challenge(room_label)
            elif command == "approve_challenge":
                self.approve_challenge(room_label, content['username'])
            elif command == "reconnect":
                self.reconnect_client()
            elif command == "refresh_chat":
                self.chat_refresh(room_label)
            elif command == "notificate_user":
                pass
            elif command == "notificate_users":
                pass
        except Exception as  error:
            await self.send_json({"action": ACTION_ERROR})

    async def reconnect_client(self):
        rooms = await self.reconnect()
        for room in rooms:
            self.rooms.add(room.label)
            await self.channel_layer.group_send(
                room.group_name,
                {
                    'type': 'chat.reconnect',
                    'label': room.label,
                    'username': self.user.username,
                    'title': room.name,
                }
            )
            await self.channel_layer.group_add(
                room.group_name,
                self.channel_layer
            )
        await self.send_json(
            {
                'action': ACTION_RECONNECT
            }
        )

    async def complete_challenge(self, label):
        room = await self.get_room(label)
        await self.channel_layer.group_send(
            room.group_name,
            {
                'type': 'chat.completechallenge',
                'label': label,
                'username': self.user.username,
                'title': room.name,
            }
        )

    async def approve_challenge(self, label, username):
        room = await self.get_room(label)
        game = await self.get_game(room, username)
        # await ?????
        is_complete = await database_sync_to_async(vote(self.userprofile, game))
        if is_complete == COMPLETED:
            self.channel_layer.group_send(
                room.group_name,
                {
                    'type': 'chat.usercompletechallenge',
                    'title': room.name,
                    'label': label,
                    'username': username,
                }
            )
        challenge = await database_sync_to_async(get_next_challenge(room))
        if challenge is not None:
            self.channel_layer.group_send(
                room.group_name,
                {
                    'type': 'chat.nextchallenge',
                    'title': room.name,
                    'label': label,
                    'challenge': 'TODO',
                }
            )

    async def disconnect(self, code):
        """called when connection is lost for client for any reason"""
        try:
            for label in self.rooms:  # could be exception?
                await self.leave_room(label)
        except:
            pass

    async def message_send(self, message, label):
        if label not in self.rooms:
            raise Exception("Room access denied")
        room = await self.get_room(label)
        await self.save_message(message)
        await self.channel_layer.group_send(
            room.group_name,
            {
                'type': 'chat.message',
                'label': label,
                'username': self.user.username,
                'message': message,
                'title': room.name,
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
                'username': self.user.username,
                'title': room.name,
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
            'action': ACTION_JOIN,
            'title': room.name,
            'label': label,
        })

        # check that room is full and if so then start games and send clients challenge
        challenge = await self.is_ready_to_start(label)
        if challenge is not None:
            await  self.channel_layer.group_send(
                room.group_name,
                {
                    'type': 'chat.nextchallenge',
                    'label': label,
                    'title': room.name,
                    'challenge': 'TODO',  # TODO add serialized data after merge
                }
            )

    async def leave_room(self, label):
        """
        called when someone leave_room
        """
        user = self.user
        room = await self.get_room(label)

        await self.channel_layer.group_send(
            room.group_name,
            {
                'type': 'chat.leave',
                'label': label,
                'username': user.username,
                'title': room.name,
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

    async def quit_room(self, label):
        """
        Not just leave room.Exit from this room if game not started yet
        """
        room = await self.get_room(label)
        if not room.is_ready:
            await self.exit_room(room)
            self.rooms.discard(label)
            await self.channel_layer.discard(
                room.group_name,
                self.channel_name
            )
            await self.channel_layer.group_send(
                room.group_name,
                {
                    'type': 'chat.quit',
                    'label': label,
                    'username': self.user.username,
                    'title': room.name,
                }
            )
        else:
            self.send_json(
                {
                    'action': ACTION_DENIED,
                    'label': label,
                    'title': room.name,
                }
            )

    async def chat_leave(self, event):
        """Called when someone leave chat aka went offline"""
        await self.send_json(
            {
                'username': event['username'],
                'msg_type': MSG_LEAVE,
                'label': event['label'],
                'title': event['title'],
                'action': ACTION_WENT_OFFLINE,
            }
        )

    async def chat_join(self, event):
        """Called when someone enter a  chat"""
        await self.send_json(
            {
                'username': event['username'],
                'msg_type': MSG_JOIN,
                'label': event['label'],
                'action': ACTION_JOIN,
                'title': event['title'],
            }
        )

    async def chat_message(self, event):
        """Called when someone send a message in room"""
        await self.send_json(
            {
                'username': event['username'],
                'msg_type': MSG_MESSAGE,
                'label': event['label'],
                'message': event['message'],
                'title': event['title'],
                'action': ACTION_MESSAGE,
            }
        )

    async def chat_nextchallenge(self, event):
        """
        Called when all users completed challenge and need fetch next challenge
        """
        await self.send_json(
            {
                'challenge': event['challenge'],
                'label': event['label'],
                'title': event['title'],
                'msg_type': MSG_ALERT,
                'action': ACTION_COMPLETE,
            }
        )

    async def chat_usercompletechallenge(self, event):
        """
        Called when someone complete challenge
        """
        await self.send_json(
            {
                'label': event['label'],
                'title': event['title'],
                'msg_type': MSG_ALERT,
                'action': ACTION_USER_COMPLETE,
                'username': event['username']
            }
        )

        # TODO send all users in room that game start and that 's a new challenge to complete

    async def chat_completechallenge(self, event):
        """
        Called when someone claim to accept that he complete challenge
        """
        await self.send_json(
            {
                'label': event['label'],
                'title': event['title'],
                'msg_type': MSG_ALERT,
                'action': ACTION_APPROVE,
                'username': event['username']
            }
        )

    async def chat_quit(self, event):
        """
        Called when when someone exit room
        """
        await self.send_json(
            {
                'label': event['label'],
                'msg_type': MSG_ALERT,
                'title': event['title'],
                'username': event['username'],
                'action': ACTION_QUIT,
            }
        )

    async def chat_reconnect(self, event):
        """
        Called when someone reconnect to room
        """
        await self.send_json(
            {
                'label': event['label'],
                'msg_type': MSG_JOIN,
                'title': event['title'],
                'username': event['username'],
                'action': ACTION_ONLINE,
            }
        )

    async def chat_refresh(self, label):
        """
        Called when someone want refresh chat
        """
        room = await self.get_room(label)
        messages = await self.fetch_all_message(room)
        await self.send_json(
            {
                'messages': messages,
                'action': ACTION_REFRESH_CHAT,
                'label': label,
                'title': room.name
            }
        )

    # helpers with interaction with db

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
            # room already full
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
    def fetch_messages(self, label, size, startwith=0):
        """
        Fetch n messages from specific room startwith k message aka get history
        :param label:
        :param startwith:
        :param size:
        :return:
        """
        messages = Room.objects.get(label=label).messages.order_by('-created')[startwith:size]
        messages = MessageSerializers(messages, many=True)
        return messages.data

    @database_sync_to_async
    def fetch_all_message(self, room):
        # for recycler viewer
        messages = room.messages.order_by('-created')
        messages = MessageSerializers(messages, many=True)
        return messages.data

    @database_sync_to_async
    def reconnect(self):
        return UserProfile(self.userprofile).rooms.all()

    @database_sync_to_async
    def is_ready_to_start(self, label):
        """
        Check that room is full and if so then start games
        """
        room = Room.objects.filter(label=label)
        if not room.is_ready and room.size <= room.users.count():
            room.update(is_ready=True)
            return prepare_game(room)

    @database_sync_to_async
    def exit_room(self, room):
        room.users.remove(self.userprofile)

    @database_sync_to_async
    def get_game(self, room, username):
        return room.current_games.get(jury__user__username=username)
