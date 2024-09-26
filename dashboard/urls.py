from __future__ import unicode_literals
from django.conf.urls import url

from pttrack.urls import wrap_url
from . import views

unwrapped_urlconf = [
    url(r'^dispatch/$',
        views.dashboard_dispatch,
        name='dashboard-dispatch'),
    url(r'^attending/$',
        views.dashboard_attending,
        name='dashboard-attending'),
    url(r'^volunteer/$',
    	views.dashboard_volunteer,
    	name='dashboard-volunteer')
]

urlpatterns = [wrap_url(u, **{}) for u in unwrapped_urlconf]
