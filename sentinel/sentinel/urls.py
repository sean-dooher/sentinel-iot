from django.conf.urls import url, include
from django.urls import path
from django.contrib import admin
from frontend.views import index, login_view, logout_view, dashboard, register, demo
from hub.views import register_leaf, HubList, HubDetail
from hub.views import LeafList, LeafDetail, DatastoreDetail, DatastoreList, ConditionList, ConditionDetail
from hub.views import demo_conditions, demo_datastores, demo_leaves, demo_hub, demo_denied
from rest_framework.urlpatterns import format_suffix_patterns

urlpatterns = [
    path(r'admin/', admin.site.urls),
    path(r'api/hub/', HubList.as_view()),
    path(r'api/hub/<int:id>/', HubDetail.as_view()),
    path(r'api/hub/<int:id>/leaves/<uuid:uuid>', LeafDetail.as_view()),
    path(r'api/hub/<int:id>/leaves/', LeafList.as_view()),
    path(r'api/hub/<int:id>/datastores/<name>', DatastoreDetail.as_view()),
    path(r'api/hub/<int:id>/datastores/', DatastoreList.as_view()),
    path(r'api/hub/<int:id>/conditions/<name>', ConditionDetail.as_view()),
    path(r'api/hub/<int:id>/conditions/', ConditionList.as_view()),
    path(r'', index, name='index'),
    path(r'register/', register,  name='register'),
    path(r'accounts/login/', login_view,  name='login'),
    path(r'accounts/logout/', logout_view, name='logout'),
    path(r'dashboard/', dashboard, name='dashboard'),
    path(r'o/', include('oauth2_provider.urls', namespace='oauth2_provider')),
    path(r'hub/<int:id>/register', register_leaf),
]

demo_urls = [
    path(r'demo/', demo),
    path(r'demo/api/hub/', demo_hub),
    path(r'demo/api/hub/<int:id>/leaves/', demo_leaves),
    path(r'demo/api/hub/<int:id>/datastores/', demo_datastores),
    path(r'demo/api/hub/<int:id>/conditions/', demo_conditions),
    url(r'demo/api/hub/[^/]+/[^/]+/[^/]+', demo_denied),  # for leaf, datastores, conditions details
    url(r'demo/api/hub/[^/]+/$', demo_denied),  # for hub details
]

urlpatterns += demo_urls

urlpatterns = format_suffix_patterns(urlpatterns)