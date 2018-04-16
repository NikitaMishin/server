"""server URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path
from rest_framework import routers
from chat.views import RoomViewSet, UserViewSet, RoomCategoryViewSet, UserProfileViewSet, get_followers_info, \
    relationship_action
from django.conf.urls import url, include

from chat import urls
from chat import views

# that u can see who in chat room



router = routers.DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'rooms', RoomViewSet)
router.register(r'category', RoomCategoryViewSet)
router.register(r'user_profiles', UserProfileViewSet)

from django.conf.urls import include, url
from django.contrib import admin

from rest_framework_jwt.views import obtain_jwt_token
from rest_framework_jwt.views import refresh_jwt_token
from rest_framework_jwt.views import verify_jwt_token

from  django.conf.urls.static import static
from django.conf import settings

from  chat.auth import auth_by_access_token
from chat.views import logout_user

urlpatterns = [
                  # chat
                  url(r'^ws/chat/', include('chat.urls')),
                  # category,room,userpofiles
                  url(r'^w1.0/', include(router.urls)),
                  url(r'^w1.0/get_following/', get_followers_info),
                  # auth
                  url(r'^auth/auth-jwt/', obtain_jwt_token),
                  url(r'^auth/auth-jwt-refresh/', refresh_jwt_token),
                  url(r'^auth/auth-jwt-verify', verify_jwt_token),
                  url(r'^auth/auth-by-access-token/(?P<backend>[^/]+)/$', auth_by_access_token),
                  url(r'auth/logout/', logout_user),
                  path('admin/', admin.site.urls),
              ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
