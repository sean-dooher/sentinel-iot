from django.conf.urls import url, include
from django.contrib import admin
from frontend.views import index, login_view, logout_view, dashboard, register
from hub.views import fake_in, fake_out, rfid_demo, main,  HubList, HubDetail
from hub.views import LeafList, LeafDetail, DatastoreDetail, DatastoreList, ConditionList, ConditionDetail
from rest_framework.urlpatterns import format_suffix_patterns

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^api/hub/$', HubList.as_view()),
    url(r'^api/hub/(?P<id>[^/]+)/$', HubDetail.as_view()),
    url(r'^api/hub/(?P<id>[^/]+)/leaves/(?P<uuid>[0-9a-f]{8}(?:-{0,1}[0-9a-f]{4}){3}-{0,1}[0-9a-f]{12})$', LeafDetail.as_view()),
    url(r'^api/hub/(?P<id>[^/]+)/leaves', LeafList.as_view()),
    url(r'^api/hub/(?P<id>[^/]+)/datastores/(?P<name>[0-9_a-z\-]+)', DatastoreDetail.as_view()),
    url(r'^api/hub/(?P<id>[^/]+)/datastores', DatastoreList.as_view()),
    url(r'^api/hub/(?P<id>[^/]+)/conditions/(?P<name>[0-9_a-z\-]+)', ConditionDetail.as_view()),
    url(r'^api/hub/(?P<id>[^/]+)/conditions', ConditionList.as_view()),
    url(r'^$', index, name='index'),
    url(r'^register/$', register,  name='register'),
    url(r'^login/$', login_view,  name='login'),
    url(r'^logout/$', logout_view, name='logout'),
    url(r'^hub/dashboard/$', dashboard, name='dashboard'),
    url(r'^o/', include('oauth2_provider.urls', namespace='oauth2_provider')),
    url(r'hub/(?P<id>[^/]+)/fake_in$', fake_in),
    url(r'hub/(?P<id>[^/]+)/fake_out$', fake_out),
]

urlpatterns = format_suffix_patterns(urlpatterns)