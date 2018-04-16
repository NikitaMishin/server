from rest_framework import serializers
from .models import Challenge, CategoryChallenge


class ChallengeCategorySearchSerializers(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = CategoryChallenge
        fields = ('name', )


class ChallengeSearchSerializers(serializers.HyperlinkedModelSerializer):
    category_challenge = ChallengeCategorySearchSerializers(many=True)

    class Meta:
        model = Challenge
        fields = ('name', 'category_challenge', 'url')
