from __future__ import unicode_literals
from django.conf.urls import url
from pttrack.urls import wrap_url

from . import views

unwrapped_urlconf = [  # pylint: disable=invalid-name
    url(r'^$',
        views.index,
        name='visualization-main'),
]

wrap_config = {}
urlpatterns = [wrap_url(url, **wrap_config) for url in unwrapped_urlconf]