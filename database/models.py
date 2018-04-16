from __future__ import unicode_literals
from django.db import models
from django.utils import timezone


class CategoryChallenge(models.Model):
    name = models.CharField(max_length=200)
    description = models.CharField(max_length=500)

    def __str__(self):
        return self.name


class PlotChallenge(models.Model):
    name = models.CharField(max_length=200)
    description = models.CharField(max_length=500)
    challenge_creator = models.ForeignKey('chat.UserProfile', on_delete=False)

    def __str__(self):
        return self.name


# unique-True
class Challenge(models.Model):
    name = models.CharField(max_length=200, default='challenge_name')
    category_challenge = models.ManyToManyField(CategoryChallenge, 'challenge_category', blank=True)
    pub_date = models.DateTimeField('date published', default=timezone.now)
    edit_date = models.DateTimeField('date edited', default=timezone.now)
    description = models.CharField(max_length=500)
    popularity = models.PositiveSmallIntegerField(default=0)
    cost = models.PositiveSmallIntegerField(default=100)
    plot_challenge = models.ManyToManyField(PlotChallenge, 'plot_challenge', blank=True)
    challenge_creator = models.ForeignKey('chat.UserProfile', on_delete=False)
    difficulty = models.PositiveSmallIntegerField(default=100)

    def __str__(self):
        return self.name
