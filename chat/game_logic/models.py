from django.db import models
from django.utils import timezone

from chat.models import UserProfile
from database.models import Challenge

PRICE = 2.0
COMPLETED = 1
NOT_COMPLETED = 0
APPROVE = True
REJECT = False

"""
    Description:
    
    When users get a challenge inside the room
    for each user will be created Game where other is jury

"""

# When delete? always in 00:00 filter  where is_finished ==True - delete
class Game(models.Model):
    user = UserProfile
    challenge = Challenge
    jury = models.ManyToManyField(UserProfile, related_name='games')
    votes_to_approve = models.IntegerField(default=1)
    approved = models.ManyToManyField(UserProfile, None)
    is_finished = models.BooleanField(default=False)
    created = models.DateTimeField(default=timezone.now())


from django.db.models import F


def vote(judge, game):
    '''
    :param judge:
    :param game:
    :return:
    '''

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
