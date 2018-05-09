from django.contrib.auth import login
from rest_framework.decorators import api_view
from rest_framework.response import Response
from social_django.utils import psa

from rest_framework_jwt.settings import api_settings

payload_handler = api_settings.JWT_PAYLOAD_HANDLER
encode_handler = api_settings.JWT_ENCODE_HANDLER

##@dra()
@psa()
@api_view(['GET'])
def auth_by_access_token(request, backend):
    try:
        token = request.GET.get('access_token')
        user = request.backend.do_auth(token)
        if user:
            login(request, user)
            payload = payload_handler(user)
            token = encode_handler(payload)
            return Response(data={'token': token}, status=200)
        else:
            return Response(data={'token': None}, status=404)
    except ValueError:
        return Response(data={'error': 'Credentials are not provided'}, status=401)
