from django.test import TestCase
from django.test import Client
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User

from pttrack.models import ProviderType

from .models import PageviewRecord


class TestAudit(TestCase):

    fixtures = ['pttrack.json']

    def setUp(self):
        self.client = Client()

    def test_audit_unicode(self):
        """Check that unicode works for TestAudit
        """
        p = PageviewRecord.objects.create(
            user=User.objects.first(),
            user_ip='128.0.0.1',
            role=ProviderType.objects.first(),
            method=PageviewRecord.HTTP_METHODS[0],
            url=reverse('home'),
            referrer='',
            status_code=200,
        )

        self.assertEquals(
            str(p),
            "GET by None to /pttrack/ at %s" % p.timestamp)

    def test_create_on_view(self):
        self.client.get(reverse('home'))

        n_records = PageviewRecord.objects.count()
        self.assertEquals(n_records, 1)
