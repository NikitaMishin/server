from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from rest_framework.generics import CreateAPIView
from rest_framework.mixins import RetrieveModelMixin, UpdateModelMixin
from rest_framework.permissions import IsAuthenticated
from rest_framework.status import HTTP_201_CREATED, HTTP_400_BAD_REQUEST
from rest_framework.viewsets import GenericViewSet

from .models import Room, Message, RoomCategory, UserProfile, Relationship

from django_filters.rest_framework import DjangoFilterBackend

from rest_framework import viewsets, filters, permissions
from .serializers import PersonSerializers, RoomSerializers, MessageSerializers, RoomCategorySerializers, RoomCategory, \
    UserProfileSerializer, RoomSearchSerializers, UserSearchSerializers, UserInfo, CleintUserProfileSerializer
# RestrictUserProfile
# Create your views here.

from django.contrib.auth.models import User
from rest_framework.renderers import JSONRenderer
from rest_framework.parsers import JSONParser, FormParser, MultiPartParser
from rest_framework.decorators import api_view, detail_route, parser_classes
from rest_framework.response import Response
from rest_framework import status


# @api_view(['GET'])
# def category_rooms(request, label):
#    rooms = RoomCategory.objects.get(name=label).rooms.order_by('-name')
#    rooms = RoomCategorySerializers(rooms, many=True)
#    return Response({'rooms': rooms.data}, status=status.HTTP_200_OK)


# @api_view(['GET'])
# def chat_room(request, label):
#  room, created = Room.objects.get_or_create(label=label)
# messages = reversed(room.messages.order_by('-created'))
# room = RoomSerializers(room)
# messages = MessageSerializers(messages,many=True)
# return Response({'room':room.data,'messages':messages.data},status=status.HTTP_200_OK)

class RoomListView(viewsets.ModelViewSet):
    queryset = Room.objects.all()
    serializer_class = RoomSearchSerializers
    filter_backends = (DjangoFilterBackend, filters.OrderingFilter)
    filter_fields = ('name', 'category__name')
    ordering = ('-expiry',)
    permission_classes = (IsAuthenticated,)


class UserListView(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSearchSerializers
    filter_backends = (DjangoFilterBackend, filters.OrderingFilter)
    filter_fields = ('username', 'email', 'last_name', 'first_name')
    ordering = ('-date_joined',)
    permission_classes = (IsAuthenticated,)


class UserViewSet(viewsets.ModelViewSet):
    """
      API endpoint that allows users to be viewed or edited.
      """
    permission_classes = (IsAuthenticated,)
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = PersonSerializers


class CreateUserView(CreateAPIView):
    model = User
    permission_classes = [
        permissions.AllowAny  # Or anon users can't register
    ]
    serializer_class = UserInfo


class RoomViewSet(viewsets.ModelViewSet):
    """
     API endpoint that allows rooms to be viewed or edited.
     """
    permission_classes = (IsAuthenticated,)

    queryset = Room.objects.all()
    serializer_class = RoomSerializers


class RoomCategoryViewSet(viewsets.ModelViewSet):
    """
    Api endpoint that allows different category of rooms be viewed or edited
    """
    permission_classes = (IsAuthenticated,)

    queryset = RoomCategory.objects.all()
    serializer_class = RoomCategorySerializers


from .permissions import IsAdminOrIsSelf


class UserProfileViewSet(RetrieveModelMixin, UpdateModelMixin, GenericViewSet):
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer
    permission_classes = (IsAdminOrIsSelf,)

    @detail_route(methods=["POST"], permission_classes=[IsAdminOrIsSelf])
    @parser_classes((FormParser, MultiPartParser,))
    def image(self, request, *args, **kwargs):
        if 'upload' in request.data:
            user_profile = self.get_object()
            user_profile.image.delete()
            upload = request.data['upload']
            user_profile.image.save(upload.name, upload)
            return Response(status=HTTP_201_CREATED, headers={'Location': user_profile.image.url})
        else:
            return Response(status=HTTP_400_BAD_REQUEST)


from django.shortcuts import render
from django.utils.safestring import mark_safe
import json


def index(request):
    return render(request, 'chat/index.html', {})


def room(request, room_name):
    return render(request, 'chat/room.html', {
        'room_name_json': mark_safe(json.dumps(room_name))
    })


@api_view(['GET'])
@login_required()
def get_followers_info(request):
    user = request.user
    followers = UserProfileSerializer(data=user.userprofile.get_followers(), many=True, context={'request': request})
    following = UserProfileSerializer(data=user.userprofile.get_following(), many=True, context={'request': request})
    friends = UserProfileSerializer(data=user.userprofile.get_friends(), many=True, context={'request': request})
    followers.is_valid()  # bad
    following.is_valid()  # bad
    friends.is_valid()  # TODO bad hadrcoded
    return Response(data={'followers': followers.data, 'following': following.data, 'friends': friends.data},
                    status=200)


from .models import RELATIONSHIP_FOLLOWING, RELATIONSHIP_BLOCKED, RELATIONSHIP_STOP_FOLLOW

START_FOLLOW = str(RELATIONSHIP_FOLLOWING)
BLOCK_FOLLOW = str(RELATIONSHIP_BLOCKED)
END_FOLLOW = str(RELATIONSHIP_STOP_FOLLOW)


# to start follow or remove follow or block user
@api_view(['GET'])
@login_required()
def relationship_action(request, action, id):
    pass
    # try:
    # user = UserProfile.objects.get(id=id)
    # if action == START_FOLLOW:
    #     relationship = Relationship.objects.filter(to_person=user,from_person=request.user)
    #      relationship.
    #   elif action == END_FOLLOW:
    #    print(END_FOLLOW)
    # elif action == BLOCK_FOLLOW:
    #   print(BLOCK_FOLLOW)
    # except Exception:
    # return Response()

    ###see friends
    ### see followers
    ### see whom following
    ### start following
    ### end following
    ###start chat
    ### join room
    ### leave room
    ### search room (aka nice filters)
    ###for one -to one challenge
    ###get my achievements
    ### get my current room
    ### like challenge
    ### create room
    ### create challenge


@api_view(['GET'])
def logout_user(request):
    from django.contrib.auth import logout
    logout(request)
    return Response(status=200, data={'message': 'logout'})

##hardcoded
@api_view(('GET',))
def get_user_profile(request, username):
    try:
        id  = User.objects.get(username= username).id
        return redirect("http://hserver.leningradskaya105.ru:6379/w1.0/user_profiles/w1.0/user_profiles/"+str(id))
    except Exception as error:
        return Response(status=400)
