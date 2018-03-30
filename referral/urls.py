from django.conf.urls import url
from pttrack.urls import wrap_url
from . import views

unwrapped_urlconf = [  # pylint: disable=invalid-name
    url(r'^new-referral/(?P<pt_id>[0-9]+)/(?P<rtype>[\w]+)$',
        views.ReferralCreate.as_view(),
        name='new-referral'),
    url(r'^followup-request/(?P<pt_id>[0-9]+)/(?P<referral_id>[0-9]+)$',
        views.FollowupRequestCreate.as_view(),
        name='new-followup-request'),
    url(r'^patient-contact/(?P<pt_id>[0-9]+)/(?P<referral_id>[0-9]+)/(?P<followup_id>[0-9]+)$',
        views.PatientContactCreate.as_view(),
        name='new-patient-contact'),
    url(r'^select-referral/(?P<pt_id>[0-9]+)$',
        views.select_referral,
        name='select-referral'),
    url(r'^select-referral-type/(?P<pt_id>[0-9]+)$',
        views.select_referral_type,
        name='select-referral-type')
]

wrap_config = {}
urlpatterns = [wrap_url(url, **wrap_config) for url in unwrapped_urlconf]