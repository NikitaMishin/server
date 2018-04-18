
import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import datetime

DEBUG = True

ALLOWED_HOSTS = ['*']


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'nasdb',
        'USER': 'nas',
        'PASSWORD': 'little_nastya',
        'HOST': 'hserver.leningradskaya105.ru',
        'PORT': '8000',
    }
}
