# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin


from .models import Person, CategoryChallenge, PlotChallenge, Challenge

# Register your models here.

admin.site.register(Person)

admin.site.register(CategoryChallenge)

admin.site.register(PlotChallenge)

admin.site.register(Challenge)
