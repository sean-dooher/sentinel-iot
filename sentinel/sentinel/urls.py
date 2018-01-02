"""sentinel URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin
from hub.views import fake_in, fake_out, rfid_demo, main,  HubList, HubDetail
from hub.views import LeafList, LeafDetail, DatastoreDetail, DatastoreList, ConditionList, ConditionDetail
from rest_framework.urlpatterns import format_suffix_patterns
from hub.utils import disconnect_all


urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^hub/(?P<id>[^/]+)/main/$', main),
    url(r'^hub/(?P<id>[^/]+)/fake_in/$', fake_in),
    url(r'^hub/(?P<id>[^/]+)/fake_out/$', fake_out),
    url(r'^hub/(?P<id>[^/]+)/rfid_demo/$', rfid_demo),
    url(r'hub/$', HubList.as_view()),
    url(r'hub/(?P<id>[^/]+)/$', HubDetail.as_view()),
    url(r'hub/(?P<id>[^/]+)/leaves/(?P<uuid>[0-9a-f]{8}(?:-{0,1}[0-9a-f]{4}){3}-{0,1}[0-9a-f]{12})$', LeafDetail.as_view()),
    url(r'^hub/(?P<id>[^/]+)/leaves', LeafList.as_view()),
    url(r'^hub/(?P<id>[^/]+)/datastores/(?P<name>[0-9_a-z\-]+)', DatastoreDetail.as_view()),
    url(r'^hub/(?P<id>[^/]+)/datastores', DatastoreList.as_view()),
    url(r'^hub/(?P<id>[^/]+)/conditions/(?P<name>[0-9_a-z\-]+)', ConditionDetail.as_view()),
    url(r'^hub/(?P<id>[^/]+)/conditions', ConditionList.as_view())
]
urlpatterns = format_suffix_patterns(urlpatterns)

# disconnect_all()
