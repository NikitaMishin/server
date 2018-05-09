from rest_framework.permissions import IsAuthenticated

from .models import Challenge

from django_filters.rest_framework import DjangoFilterBackend

from rest_framework import viewsets, filters
from .serializers import ChallengeSearchSerializers


class ChallengeListView(viewsets.ModelViewSet):
    queryset = Challenge.objects.all()
    serializer_class = ChallengeSearchSerializers
    filter_backends = (DjangoFilterBackend, filters.OrderingFilter)
    filter_fields = ('name', 'category_challenge__name')
    ordering = ('-pub_date',)
    permission_classes = (IsAuthenticated,)
