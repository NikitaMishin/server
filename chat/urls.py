from django.conf.urls import url
from rest_framework.urlpatterns import format_suffix_patterns
from chat import views


urlpatterns = [
  url(r'^$',views.index,name='index'),
  url(r'^(?P<room_name>[^/]+)/$',views.room,name='room')

]

urlpatterns = format_suffix_patterns(urlpatterns)