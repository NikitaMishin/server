from rest_framework import serializers

from .models import Room, Message, RoomCategory, UserProfile
from django.contrib.auth.models import User

# TODO add extra fields and extend model


class RoomSearchSerializers(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Room
        fields = ('name', 'category', 'url')


class UserSearchSerializers(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'email', 'last_name', 'first_name', 'url')


class RoomSerializers(serializers.HyperlinkedModelSerializer):
    # messages = serializers.StringRelatedField(many=True)
    class Meta:
        model = Room
        fields = ('name', 'label', 'url')  # ,'messages'


class RoomCategorySerializers(serializers.HyperlinkedModelSerializer):
    rooms = RoomSerializers(many=True)

    class Meta:
        model = RoomCategory
        fields = ('name', 'rooms', 'url')


class PersonSerializers(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ('email', 'username', 'url', 'userprofile')


class MessageSerializers(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = '__all__'


class UserInfo(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'email', 'last_name', 'first_name')


class UserProfileSerializer(serializers.HyperlinkedModelSerializer):
    user = UserInfo()

    class Meta:
        model = UserProfile
        fields = ('url', 'birth_date', 'image', 'gender', 'bio', 'user')  # related_to - how folliwing
        read_only_fields = ('url', 'image')
