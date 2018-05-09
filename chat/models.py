from django.conf import settings
from django.template.defaultfilters import slugify
from django.utils import timezone

from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from  database.models import Challenge

from database.models import  CHAR_SIZE_LIMITED,DESCRIPTION_SIZE_LIMITED

DESCRIPTION_SIZE = DESCRIPTION_SIZE_LIMITED
MAX_ROOM_NAME_LENGTH = CHAR_SIZE_LIMITED



GENDER_UNKNOWN = 'U'
GENDER_MALE = 'M'
GENDER_FEMALE = 'F'
GENDER_CHOICES = (
    (GENDER_UNKNOWN, 'unknown'),
    (GENDER_MALE, 'male'),
    (GENDER_FEMALE, 'female'),
)
RELATIONSHIP_STOP_FOLLOW = 0
RELATIONSHIP_FOLLOWING = 1
RELATIONSHIP_BLOCKED = 2
RELATIONSHIP_STATUS = (
    (RELATIONSHIP_FOLLOWING, 'Following'),
    (RELATIONSHIP_BLOCKED, 'Blocked')
)


def upload_to(instance, filename):
    return 'user_profile_image/{}/{}'.format(instance.user_id, filename)


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    relationship = models.ManyToManyField('self', through='Relationship',
                                          symmetrical=False,
                                          related_name='related_to')
    birth_date = models.DateField(blank=True, null=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, default=GENDER_UNKNOWN)
    bio = models.TextField(blank=True, max_length=1000)
    image = models.ImageField(blank=True, null=True, upload_to=upload_to)
    completed_challenges_online = models.ManyToManyField(Challenge, related_name='users', blank=True)
    completed_challenges_offline = models.ManyToManyField(Challenge, related_name='users_offline', blank=True)
    global_rating = models.IntegerField(default=0)
    personal_rating = models.IntegerField(default=0)  # AKA WEEK?
    is_banned = models.BooleanField(default=False)
    popularity = models.PositiveSmallIntegerField(default=0)

    def get_relationships(self, status):
        return self.relationship.filter(
            to_people__status=status,
            to_people__from_person=self
        )

    def get_related_to(self, status):
        return self.related_to.filter(
            from_people__status=status,
            from_people__to_person=self
        )

    def get_following(self):
        return self.get_relationships(RELATIONSHIP_FOLLOWING)

    def get_followers(self):
        return self.get_related_to(RELATIONSHIP_FOLLOWING)

    def get_friends(self):
        return self.relationship.filter(
            to_people__status=RELATIONSHIP_FOLLOWING,
            to_people__from_person=self,
            from_people__status=RELATIONSHIP_FOLLOWING,
            from_people__to_person=self,
        )

    def __str__(self):
        return self.user.username


class RoomCategory(models.Model):
    name = models.CharField(max_length=MAX_ROOM_NAME_LENGTH, default='unsubs', unique=True)
    description = models.TextField(max_length=DESCRIPTION_SIZE)

    def __str__(self):
        return self.name


class Room(models.Model):
    name = models.CharField(max_length=MAX_ROOM_NAME_LENGTH)
    label = models.SlugField(unique=True)
    users = models.ManyToManyField(UserProfile, related_name='rooms')  # how in this room
    challenges = models.ManyToManyField(Challenge, related_name='rooms', blank=True)  # what challenge in this room
    category = models.ForeignKey(RoomCategory, on_delete=False, related_name='rooms', null=True, blank=True)
    expiry = models.DateTimeField(blank=False,
                                  default=timezone.now() + timezone.timedelta(days=2))  # for 1-1 chat forever
    size = models.IntegerField(null=False)
    is_finished = models.BooleanField(default=False)
    is_ready = models.BooleanField(default=False)

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        if not self.id:
            self.label = slugify(self.name)
        super(Room, self).save(force_insert, force_update, using, update_fields)

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
    message = models.TextField(max_length=DESCRIPTION_SIZE)
    user = models.ForeignKey(UserProfile, on_delete=False)  # insert out custom user
    created = models.DateTimeField(default=timezone.now)  # ,db_index=True - for optimization?
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return self.message


# move rooms after expiration day reached to this model -aka history
class ExpiredRoom(models.Model):
    size = models.PositiveIntegerField(blank=False)
    challenges = models.ManyToManyField(Challenge, 'expired_rooms')
    users = models.ManyToManyField(UserProfile, related_name='expired_rooms')
    name = models.CharField(max_length=MAX_ROOM_NAME_LENGTH)
    label = models.SlugField(unique=True)
    category = models.ForeignKey(RoomCategory, on_delete=False, related_name='expired_rooms', null=True)
    is_finished = models.BooleanField(default=True)
    """
    Пользователья заходит в приложение.входит
    Клиент получает от сервера список всех текуших закрытых комнат, в которых он сейчас играет
    по веб сокету он ко всем подключается которые еще не окончены
    которые окончены- можно в истории глянуть
    
    
    """


class Relationship(models.Model):
    from_person = models.ForeignKey(UserProfile, related_name='from_people', on_delete=False)
    to_person = models.ForeignKey(UserProfile, related_name='to_people', on_delete=False)
    status = models.IntegerField(choices=RELATIONSHIP_STATUS)

    def add_relationship(self, person, status):
        relationship, created = Relationship.objects.get_or_create(
            from_person=self,
            to_person=person,
            status=status
        )
        return relationship

    def remove_relationship(self, person, status):
        Relationship.objects.filter(from_person=self, to_person=person, status=status).delete()

    def __str__(self):
        return 'from ' + self.from_person.user.username + ' to ' + self.to_person.user.username


# signals for action save and update  when used user model
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.userprofile.save()
