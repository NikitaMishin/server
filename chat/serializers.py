from rest_framework import serializers

from .models import Room, Message, RoomCategory, UserProfile
from django.contrib.auth.models import User


class UserInfo(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'last_name', 'first_name', 'password')

    def create(self, validated_data):
        user = User.objects.create(
            username=validated_data['username'],

        )
        user.set_password(validated_data['password'])
        user.save()

        return user


class UserProfileSerializer(serializers.HyperlinkedModelSerializer):
    user = UserInfo()

    class Meta:
        model = UserProfile
        fields = ('url', 'birth_date', 'image', 'gender', 'bio', 'user','global_rating','popularity')  # related_to - how folliwing
        read_only_fields = ('url', 'image')



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
    users = UserProfileSerializer(many=True, read_only=True)

    class Meta:
        model = Room
        fields = ('name', 'label', 'url', 'size', 'users', 'expiry', 'category')
        read_only_fields = ('label', 'users')


class RoomCategorySerializers(serializers.HyperlinkedModelSerializer):
    rooms = RoomSerializers(many=True, read_only=True)

    class Meta:
        model = RoomCategory
        fields = ('name', 'rooms', 'url', 'description')


class PersonSerializers(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ('email', 'username', 'url', 'userprofile')


class MessageSerializers(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = '__all__'
