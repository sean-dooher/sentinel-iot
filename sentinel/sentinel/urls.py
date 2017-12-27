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
from hub.views import fake_in, fake_out, rfid_demo
from hub.views import leaf_list, leaf_detail, datastore_list, condition_list, condition_detail
from rest_framework.urlpatterns import format_suffix_patterns

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^$', rfid_demo),
    url(r'^fake_in/$', fake_in),
    url(r'^fake_out/$', fake_out),
    url(r'^rfid_demo/$', rfid_demo),
    url(r'^leaves/(?P<uuid>[0-9a-f]{8}(?:-{0,1}[0-9a-f]{4}){3}-{0,1}[0-9a-f]{12})$', leaf_detail),
    url(r'^leaves', leaf_list),
    url(r'^datastores', datastore_list),
    url(r'^conditions/(?P<name>[0-9_a-z\-]+)', condition_detail),
    url(r'^conditions', condition_list)
]

urlpatterns = format_suffix_patterns(urlpatterns)
