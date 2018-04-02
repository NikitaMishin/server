from django.shortcuts import render

from .models import Room, Message, RoomCategory

from rest_framework import viewsets
from .serializers import PersonSerializers, RoomSerializers, MessageSerializers, RoomCategorySerializers, RoomCategory
# Create your views here.

from django.contrib.auth.models import User
from rest_framework.renderers import JSONRenderer
from rest_framework.parsers import JSONParser
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status


#@api_view(['GET'])
#def category_rooms(request, label):
#    rooms = RoomCategory.objects.get(name=label).rooms.order_by('-name')
#    rooms = RoomCategorySerializers(rooms, many=True)
#    return Response({'rooms': rooms.data}, status=status.HTTP_200_OK)


# @api_view(['GET'])
# def chat_room(request, label):
#   room, created = Room.objects.get_or_create(label=label)
#  messages = reversed(room.messages.order_by('-created'))
#  room = RoomSerializers(room)
#  messages = MessageSerializers(messages,many=True)
#  return Response({'room':room.data,'messages':messages.data},status=status.HTTP_200_OK)

class UserViewSet(viewsets.ModelViewSet):
    """
      API endpoint that allows users to be viewed or edited.
      """
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = PersonSerializers


class RoomViewSet(viewsets.ModelViewSet):
    """
     API endpoint that allows rooms to be viewed or edited.
     """
    queryset = Room.objects.all()
    serializer_class = RoomSerializers


class RoomCategoryViewSet(viewsets.ModelViewSet):
    """
    Api endpoint that allows different category of rooms be viewed or edited
    """
    queryset = RoomCategory.objects.all()
    serializer_class = RoomCategorySerializers


####

from django.shortcuts import render
from django.utils.safestring import mark_safe
import json


def index(request):
    return render(request, 'chat/index.html', {})


def room(request, room_name):
    return render(request, 'chat/room.html', {
        'room_name_json': mark_safe(json.dumps(room_name))
    })
