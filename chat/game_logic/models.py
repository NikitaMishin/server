from django.db import models
from django.utils import timezone

from chat.models import UserProfile, Room
from database.models import Challenge

PRICE = 2.0
COMPLETED = 1
NOT_COMPLETED = 0
APPROVE = True
REJECT = False

"""
    Description:

"""


class Game(models.Model):
    user = UserProfile
    challenge = Challenge
    room = models.ForeignKey(Room, on_delete=True, related_name='current_games')
    jury = models.ManyToManyField(UserProfile, related_name='games')
    votes_to_approve = models.IntegerField(default=1)
    approved = models.ManyToManyField(UserProfile, None)
    is_finished = models.BooleanField(default=False)
    created = models.DateTimeField(default=timezone.now())


from django.db.models import F


def vote(judge, game):
    """
    Element of game.When one of jury decide to approve user challenge he vote.If half of jury accepted then user complete challnge=>
    updates some of his fields
    :param judge:
    :param game:
    :return: COMPLETED or NOT_COMPLETED
    """
    if judge not in game.approved:
        game.approved.add(judge)
    if game.approved.count() * 2 >= game.jury.count() and game.is_finished == False:
        # challenge completed
        earned = calculate_sum(game)
        game.user.completed_challenges_online.add(game.challenge)
        UserProfile.objects.filter(pk=game.user.pk).update(global_rating=F('global_rating') + earned)
        # UserProfile.objects.filter(pk=game.user.pk).update(global_rating=F('personal_rating') + earned)
        Game.objects.filter(id=game.id).update(is_finished=True)
        return COMPLETED
    else:
        return NOT_COMPLETED


def calculate_sum(game):
    return game.challenge.cost * (PRICE + game.approved.count() / 1.0)


# TODO add logic for getting distinct challenges
def prepare_game(room):
    """
    create games for users in room.
    :param room:
    :return: challenge
    """
    from random import randint
    users = room.users
    query_set = Challenge.objects.filter(category=room.category)
    challenge = query_set[randint(0, query_set.count() - 1)]
    room.challenges.add(challenge)
    for user in users:
        Game.objects.create(
            user=user,
            challenge=challenge,
            room=room,
            jury=users.exclude(pk=user.pk),
            votes_to_approve=users.count() - 1,
        )
    return challenge


def get_next_challenge(room):
    """
    Checked that all gamers successully compelete challenge ,if so then delete game and prepare another games
    :param room:
    :return: Challenge or None
    """
    current_games = room.current_games
    if current_games.count() == current_games.filter(is_finished=True):
        room.current_games.all().delete()
        return prepare_game(room)


def get_random_challenge(room):
    pass
