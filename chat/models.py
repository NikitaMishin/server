from django.utils import timezone

from django.contrib.auth.models import User
from django.db import models

MAX_MESSAGE_LENGTH = 500
MAX_ROOM_NAME_LENGTH = 255


class RoomCategory(models.Model):
    name = models.CharField(max_length=MAX_ROOM_NAME_LENGTH, default='unsubs', unique=True)

    def __str__(self):
        return self.name


class Room(models.Model):
    name = models.CharField(max_length=MAX_ROOM_NAME_LENGTH)
    label = models.SlugField(unique=True)
    category = models.ForeignKey(RoomCategory, on_delete=False, related_name='rooms', null=True)

    def __str__(self):
        return self.label

    @property
    def group_name(self):
            """
            Returns the Channels Group name that sockets should subscribe to to get sent
            messages as they are generated.
            """
            return "room-%s" % self.label


class Message(models.Model):
    room = models.ForeignKey(Room, related_name='messages', on_delete=True)
    message = models.TextField(max_length=MAX_MESSAGE_LENGTH)
    user = models.ForeignKey(User, on_delete=False)  # insert out custom user
    created = models.DateTimeField(default=timezone.now)  # ,db_index=True - for optimization?

    def __str__(self):
        return str(self.id) + str(self.user.username)


class customUser(User):
    pass
    # last_qeolocation
    # last_update
    # rating
    # achievements = models.ManyToManyField()
