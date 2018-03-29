from __future__ import unicode_literals
from django import forms
from django.contrib.auth.models import User
from django.contrib.auth import authenticate


class LoginForm(forms.Form):
    username = forms.CharField(label='Username', max_length=40, required=True, min_length=3)
    password = forms.CharField(label='Password', required=True, min_length=8)

    def save(self):
        user = authenticate(**self.cleaned_data)
        return user


class SignUpForm(forms.Form):
    first_name = forms.CharField(label='First name', max_length=40, required=False)
    last_name = forms.CharField(label='Last name', max_length=40, required=False)
    username = forms.CharField(label='Username', max_length=40, required=True, min_length=3)
    email = forms.EmailField(required=True)
    password = forms.CharField(label='Password', widget=forms.PasswordInput(), required=True, min_length=6)

    def save(self):
        user = User.objects.create_user(**self.cleaned_data)
        user.save()
        return user
