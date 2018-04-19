import os
import django
from channels.routing import get_default_application
#import channels.asgi
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")
django.setup()
application = get_default_application()
#channel_layer = channels.asgi.get_channel_layer()