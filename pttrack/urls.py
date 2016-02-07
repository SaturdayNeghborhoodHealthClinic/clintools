from django.conf.urls import url
from django.views.generic import ListView, DetailView
from django.views.generic.base import TemplateView

from django.contrib.auth.decorators import login_required

from .decorators import provider_required
from . import models as mymodels
from . import views

# pylint: disable=I0011

unwrapped_urlpatterns = [  # pylint: disable=invalid-name
    url(r'^$',
        views.home_page,
        name="home"),
    url(r'^all/$',
        views.all_patients,
        name="all-patients"),
    url(r'^refresh$',
        views.all_patients_data,
        name='refresh'),
    url(r'^phone_directory/$',
        views.phone_directory,
        name="phone-directory"),
    url(r'^intake/$',
        views.PatientCreate.as_view(),
        name="intake"),
    url(r'^(?P<pk>[0-9]+)/$',
        views.patient_detail,
        name='patient-detail'),
    url(r'^patient/update/(?P<pk>[0-9]+)$',
        views.PatientUpdate.as_view(),
        name='patient-update'),
    url(r'^patient/activate_detail/(?P<pk>[0-9]+)$',
        views.patient_activate_detail,
        name='patient-activate-detail'),
    url(r'^patient/activate_home/(?P<pk>[0-9]+)$',
        views.patient_activate_home,
        name='patient-activate-home'),


    # PROVIDERS
    url(r'^new-provider/$',
        views.ProviderCreate.as_view(),
        name='new-provider'),
    url(r'^choose-role/$',
        views.choose_clintype,
        name='choose-clintype'),

    # ACTION ITEMS
    url(r'^(?P<pt_id>[0-9]+)/action-item/$',
        views.ActionItemCreate.as_view(),
        name='new-action-item'),
    url(r'^action-item/(?P<pk>[0-9]+)/update$',
        views.ActionItemUpdate.as_view(),
        name="update-action-item"),
    url(r'^action-item/(?P<ai_id>[0-9]+)/done$',
        views.done_action_item,
        name='done-action-item'),
    url(r'^action-item/(?P<ai_id>[0-9]+)/reset$',
        views.reset_action_item,
        name='reset-action-item'),

    # DOCUMENTS
    url(r'^(?P<pt_id>[0-9]+)/document/$',
        views.DocumentCreate.as_view(),
        name="new-document"),
    url(r'^document/(?P<pk>[0-9]+)$',
        DetailView.as_view(model=mymodels.Document),
        name="document-detail"),
    url(r'^document/update/(?P<pk>[0-9]+)$',
        views.DocumentUpdate.as_view(),
        name="document-update"),

    # MISC
    url(r'^about/',
        TemplateView.as_view(template_name='pttrack/about.html'),
        name='about'),
]

def url_wrap(urls):
    '''
    Wrap URLs in login_required and provider_required decorators as
    appropriate.
    '''
    wrapped_urls = []
    for u in urls:
        if u.name in ['new-provider', 'choose-clintype']:
            # do not wrap in full regalia
            u._callback = login_required(u._callback)
        elif u.name in ['about']:
            # do not wrap at all, fully public
            pass
        else:
            u._callback = provider_required(u._callback)

        wrapped_urls.append(u)
    return wrapped_urls

urlpatterns = url_wrap(unwrapped_urlpatterns)

