from django.contrib.auth.models import AnonymousUser
from rest_framework_jwt.serializers import VerifyJSONWebTokenSerializer


class JWTAuthMiddleware:
    def __init__(self, inner):
        self.inner = inner

    def __call__(self, scope):
        try:
            #change on uri named args
            token_header = dict(scope['headers'])[b'sec-websocket-protocol'].decode().split()
            data = VerifyJSONWebTokenSerializer().validate({'token':token_header})
            scope['user'] = data['user']
        except:
            scope['user'] = AnonymousUser
        return self.inner(scope)
