from rest_framework import serializers

from .models import Room, Message
from django.contrib.auth.models import User


class RoomSerializers(serializers.HyperlinkedModelSerializer):
    #messages = serializers.StringRelatedField(many=True)

    class Meta:
        model = Room
        fields = ('name', 'label')#,'messages'


class PersonSerializers(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ('email', 'username', 'url')

class MessageSerializers(serializers.ModelSerializer):

    class Meta:
        model = Message
        fields = '__all__'