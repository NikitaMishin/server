from django.utils import timezone

from django.contrib.auth.models import User
from django.db import models

MAX_MESSAGE_LENGTH = 500
MAX_ROOM_NAME_LENGTH = 255


class Room(models.Model):
    name = models.CharField(max_length=MAX_ROOM_NAME_LENGTH)
    label = models.SlugField(unique=True)

    def __str__(self):
        return self.label


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
