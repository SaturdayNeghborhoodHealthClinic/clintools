from django.conf.urls import url
from pttrack.urls import wrap_url
from django.views.generic import DetailView

from . import models
from . import views

unwrapped_urlconf = [
    url(r'^all/(?P<pt_id>[0-9]+)/$',
        views.LabListView.as_view(),
        name="all-labs"),
    url(r'^(?P<pk>[0-9]+)/$',
        views.LabDetailView.as_view(),
        name='lab-detail'),
    url(r'^newm/(?P<lab_id>[0-9]+)/$',
        views.full_lab_create,
        name='new-full-lab'), #create all measurements assoc w/ the lab obj
    url(r'^newl/(?P<pt_id>[0-9]+)/$',
        views.lab_create,
        name='new-lab'), #create "parent" lab object
]

wrap_config = {}
urlpatterns = [wrap_url(url, **wrap_config) for url in unwrapped_urlconf]