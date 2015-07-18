from django.conf.urls import include, url
from django.contrib import admin
from django.views.generic.base import RedirectView

urlpatterns = [
    # Examples:
    # url(r'^$', 'clintools.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),
    url(r'^pttrack/', include('pttrack.urls')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^$', RedirectView.as_view(pattern_name="home", permanent=False)),
    url(r'^shib/', include('shibboleth.urls', namespace='shibboleth')),
]
