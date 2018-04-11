from django.contrib import admin

# Register your models here.
from .models import Room, Message, RoomCategory, UserProfile, ExpiredRoom, Relationship

admin.site.register(Room)

admin.site.register(Message)
admin.site.register(RoomCategory)
admin.site.register(UserProfile)
admin.site.register(ExpiredRoom)
admin.site.register(Relationship)
