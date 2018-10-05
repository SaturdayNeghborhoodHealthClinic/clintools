from django.test import TestCase
from itertools import *

from followup.models import ContactMethod, NoAptReason, NoShowReason, ContactResult
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from pttrack.models import (
    Gender, Patient, Provider, ProviderType,
    ReferralType, ReferralLocation, Note, ContactMethod, CompletableMixin,
    CompleteableManager)
#from pttrack.test_views import build_provider
import datetime
from . import forms
from . import models
from . import urls

# Create your tests here.
class TestPatientContactForm(TestCase):
    '''
    Tests the beahvior of the PatientContactForm which has a lot of
    complicated logic around valid form submission
    '''

    def setUp(self):
        ''' Provides the same context in all the tests '''

        self.contact_method = ContactMethod.objects.create(
            name="Carrier Pidgeon")
        self.pt = Patient.objects.create(
            first_name="Juggie",
            last_name="Brodeltein",
            middle_name="Bayer",
            phone='+49 178 236 5288',
            gender=Gender.objects.create(long_name="Male",
                                         short_name="M"),
            address='Schulstrasse 9',
            city='Munich',
            state='BA',
            zip_code='63108',
            pcp_preferred_zip='63018',
            date_of_birth=datetime.date(1990, 01, 01),
            patient_comfortable_with_english=False,
            preferred_contact_method=self.contact_method,
        )
        
        # Create provider because referral requires a provider
        casemanager = ProviderType.objects.create(
            long_name='Case Manager', short_name='CM',
            signs_charts=False, staff_view=True)

        user = User.objects.create_user(
            "username",
            "a@wustl.edu", "password")
        g = Gender.objects.first()
        prov = Provider.objects.create(
            first_name="Tommy", middle_name="Lee", last_name="Jones",
            phone="425-243-9115", gender=g, associated_user=user)

        reftype = ReferralType.objects.create(
            name="Specialty", is_fqhc=False)
        refloc = ReferralLocation.objects.create(
            name='COH', address='Euclid Ave.')
        refloc.care_availiable.add(reftype)

        # Note location might not work
        self.referral = models.Referral.objects.create(
            comments="Needs his back checked",
            status='P',
            kind=reftype,
            author=Provider.objects.first(),
            author_type=ProviderType.objects.first(),
            patient=self.pt
        )
        self.referral.location.add(refloc)

        # self.location = self.referral.location.create(name="COH", address="Euclid Ave")
        # self.location.save()

        self.followupRequest = models.FollowupRequest.objects.create(
            referral=self.referral,
            contact_instructions="Call him",
            due_date=datetime.date(2018, 9, 01),
            author=Provider.objects.first(),
            author_type=ProviderType.objects.first(),
            patient=self.pt
        )

        self.successful_res = ContactResult.objects.create(
            name="Got him", patient_reached=True)
        self.unsuccessful_res = ContactResult.objects.create(
            name="Disaster", patient_reached=False)
        # Need to update referral location
        self.referral_location = ReferralLocation.objects.create(
            name="Franklin's Back Adjustment",
            address="1435 Sillypants Drive")
        self.noapt_reason = NoAptReason.objects.create(
            name="better things to do")
        self.noshow_reason = NoShowReason.objects.create(
            name="Hella busy.")

    def build_form(self, contact_successful, has_appointment, apt_location,
                   noapt_reason, pt_showed, noshow_reason):
        """Utility method used to construct a PatientContactForm to suit the
        needs of the testing subroutines based upon what is provided and not
        provided.
        """
        contact_resolution = (self.successful_res if contact_successful
                              else self.unsuccessful_res)

        form_data = {
            'contact_method': self.contact_method,
            'contact_status': contact_resolution,
            'patient': self.pt,
            'referral': self.referral,
            'followupRequest': self.followupRequest
        }

        form_data['has_appointment'] = has_appointment
        form_data['pt_showed'] = pt_showed

        if apt_location:
            form_data['appointment_location'] = [ReferralLocation.objects.first().pk]

        if noapt_reason:
            form_data['no_apt_reason'] = self.noapt_reason

        if noshow_reason:
            form_data['no_show_reason'] = self.noshow_reason

        return forms.PatientContactForm(data=form_data)

    def test_has_appointment_and_pt_showed(self):
        """Verify that a provider is selected and no show and no appointment
        reasons are not selected. There are 16 cases tested here. 
        Patient showed selection can be either 'No' or 'Not yet'
        """
        # correct: pt didn't show, noshow reason is supplied
        form = self.build_form(
            contact_successful=True,
            has_appointment="Yes",
            apt_location=True,
            noapt_reason=False,
            noshow_reason=False,
            pt_showed="Yes")

        # Might want to assert a specific error
        self.assertEqual(len(form.errors), 0)

        # Create variable that holds those conditions that shouldn't lead to errors
        # apt_location = True
        # noapt_reason = False
        # noshow_reason = False
        proper_submission = (True, False, False)

        for form_field_provided in product([False, True], repeat=3):
            form = self.build_form(
                contact_successful=True,
                has_appointment="Yes",
                apt_location=form_field_provided[0],
                noapt_reason=form_field_provided[1],
                noshow_reason=form_field_provided[2],
                pt_showed="Yes")

            # Use an XOR to determine the number of differences between a
            # proper submission and the current combination of form fields
            expected_number_errors = sum(a ^ b for a, b in
                                         zip(form_field_provided,
                                             proper_submission))
            self.assertEqual(len(form.errors), expected_number_errors)


    def test_has_appointment_and_pt_no_show(self):
        """Verify that a provider is selected and a reason is provided for
        the no show. There are 16 cases tested here. Patient showed selection
        can be either 'No' or 'Not yet'
        """
        form = self.build_form(
            contact_successful=True,
            has_appointment="Yes",
            apt_location=True,
            noapt_reason=False,
            noshow_reason=True,
            pt_showed="No")

        self.assertEqual(len(form.errors), 0)

        # incorrect - no show reason is not supplied
        form = self.build_form(
            contact_successful=True,
            has_appointment="Yes",
            apt_location=True,
            noapt_reason=False,
            noshow_reason=False,
            pt_showed="No")

        self.assertEqual(len(form.errors), 1)

        # incorrect - both apt location and no apt reason are supplied
        form = self.build_form(
            contact_successful=True,
            has_appointment="Yes",
            apt_location=True,
            noapt_reason=True,
            noshow_reason=False,
            pt_showed="No")

        self.assertEqual(len(form.errors), 2)

        # incorrect - no appointment reason is supplied
        form = self.build_form(
            contact_successful=True,
            has_appointment="Yes",
            apt_location=True,
            noapt_reason=True,
            noshow_reason=True,
            pt_showed="No")

        self.assertEqual(len(form.errors), 1)

        # incorrect - appointment location is not selected
        form = self.build_form(
            contact_successful=True,
            has_appointment="Yes",
            apt_location=False,
            noapt_reason=False,
            noshow_reason=True,
            pt_showed="No")

        self.assertEqual(len(form.errors), 1)

        # incorrect - no show reason is not supplied, no apt location supplied
        form = self.build_form(
            contact_successful=True,
            has_appointment="Yes",
            apt_location=False,
            noapt_reason=False,
            noshow_reason=False,
            pt_showed="No")

        self.assertEqual(len(form.errors), 2)

        # incorrect - no apt location and no apt reason is supplied
        form = self.build_form(
            contact_successful=True,
            has_appointment="Yes",
            apt_location=False,
            noapt_reason=True,
            noshow_reason=True,
            pt_showed="No")

        self.assertEqual(len(form.errors), 2)

        # incorrect - no show reason is not supplied
        form = self.build_form(
            contact_successful=True,
            has_appointment="Yes",
            apt_location=False,
            noapt_reason=True,
            noshow_reason=False,
            pt_showed="No")

        self.assertEqual(len(form.errors), 3)

        # begin block of tests for "Not yet" for pt showed

        # correct - patient has not yet shown to clinic
        form = self.build_form(
            contact_successful=True,
            has_appointment="Yes",
            apt_location=True,
            noapt_reason=False,
            noshow_reason=False,
            pt_showed="Not yet")

        self.assertEqual(len(form.errors), 0)

        # incorrect - patient has not yet shown up to clinic,
        # no show reason is provided
        form = self.build_form(
            contact_successful=True,
            has_appointment="Yes",
            apt_location=True,
            noapt_reason=False,
            noshow_reason=True,
            pt_showed="Not yet")

        self.assertEqual(len(form.errors), 1)

        # incorrect - no appointment reason is supplied with 'Not yet'
        form = self.build_form(
            contact_successful=True,
            has_appointment="Yes",
            apt_location=True,
            noapt_reason=True,
            noshow_reason=False,
            pt_showed="Not yet")

        self.assertEqual(len(form.errors), 1)

        # incorrect - no appointment reason and no show reason is supplied
        form = self.build_form(
            contact_successful=True,
            has_appointment="Yes",
            apt_location=True,
            noapt_reason=True,
            noshow_reason=True,
            pt_showed="Not yet")

        self.assertEqual(len(form.errors), 2)

        # incorrect - no apt location and no apt reason supplied
        form = self.build_form(
            contact_successful=True,
            has_appointment="Yes",
            apt_location=False,
            noapt_reason=True,
            noshow_reason=False,
            pt_showed="Not yet")

        self.assertEqual(len(form.errors), 2)

        # incorrect - apt location not supplied, no apt reason supplied, no show reason supplied
        form = self.build_form(
            contact_successful=True,
            has_appointment="Yes",
            apt_location=False,
            noapt_reason=True,
            noshow_reason=True,
            pt_showed="Not yet")

        self.assertEqual(len(form.errors), 3)

        # incorrect - no apt location supplied
        form = self.build_form(
            contact_successful=True,
            has_appointment="Yes",
            apt_location=False,
            noapt_reason=False,
            noshow_reason=False,
            pt_showed="Not yet")

        self.assertEqual(len(form.errors), 1)

        # incorrect - no apt location supplied and no show reason supplied
        form = self.build_form(
            contact_successful=True,
            has_appointment="Yes",
            apt_location=False,
            noapt_reason=False,
            noshow_reason=True,
            pt_showed="Not yet")

        self.assertEqual(len(form.errors), 2)

    def test_no_appointment(self):
        # first form contains a proper submission for the no appointment case
        form = self.build_form(
            contact_successful=True,
            has_appointment="No",
            apt_location=False,
            noapt_reason=True,
            noshow_reason=False,
            pt_showed="No")

        self.assertEqual(len(form.errors), 0)

        # Create variable that holds those conditions that shouldn't lead to errors
        # apt_location = False
        # noapt_reason = True
        # noshow_reason = False
        proper_submission = (False, True, False)

        for form_field_provided in product([False, True], repeat=3):
            form = self.build_form(
                contact_successful=True,
                has_appointment="No",
                apt_location=form_field_provided[0],
                noapt_reason=form_field_provided[1],
                noshow_reason=form_field_provided[2],
                pt_showed="No")

            # Use an XOR to determine the number of differences between a
            # proper submission and the current combination of form fields
            expected_number_errors = sum(a ^ b for a, b in
                                         zip(form_field_provided,
                                             proper_submission))
            self.assertEqual(len(form.errors), expected_number_errors)

        # Verify that the behavior of the form is the same if user says that
        # an appointment is "Not yet" made
        for form_field_provided in product([False, True], repeat=3):
            form = self.build_form(
                contact_successful=True,
                has_appointment="Not yet",
                apt_location=form_field_provided[0],
                noapt_reason=form_field_provided[1],
                noshow_reason=form_field_provided[2],
                pt_showed="No")

            # Use an XOR to determine the number of differences between a
            # proper submission and the current combination of form fields
            expected_number_errors = sum(a ^ b for a, b in
                                         zip(form_field_provided,
                                             proper_submission))
            self.assertEqual(len(form.errors), expected_number_errors)

    def test_contact_unsuccessful(self):
        # Create a generic form
        contact_resolution = self.unsuccessful_res
        form_data = {
            'contact_method': self.contact_method,
            'contact_status': contact_resolution,
            'patient': self.pt,
            'referral': self.referral,
            'followupRequest': self.followupRequest
        }

        form = forms.PatientContactForm(data=form_data)
        self.assertEqual(len(form.errors), 0)

        # Progressively add errors to the form
        # If contact was unsuccessful, all these fields should be blank
        form_data['has_appointment'] = "Yes"
        form = forms.PatientContactForm(data=form_data)
        self.assertEqual(len(form.errors), 1)

        form_data['pt_showed'] = "Yes"
        form = forms.PatientContactForm(data=form_data)
        self.assertEqual(len(form.errors), 2)

        form_data['appointment_location'] = [ReferralLocation.objects.first().pk]
        form = forms.PatientContactForm(data=form_data)
        self.assertEqual(len(form.errors), 3)

        form_data['no_apt_reason'] = self.noapt_reason
        form = forms.PatientContactForm(data=form_data)
        self.assertEqual(len(form.errors), 4)

        form_data['no_show_reason'] = self.noshow_reason
        form = forms.PatientContactForm(data=form_data)
        self.assertEqual(len(form.errors), 5)

class TestSelectReferralType(TestCase):
    '''
    Tests the select referral type page
    '''
    fixtures = ['pttrack']

    def setUp(self):
        from pttrack.test_views import log_in_provider, build_provider
        log_in_provider(self.client, build_provider())

        self.contact_method = ContactMethod.objects.create(
            name="Carrier Pidgeon")

        self.pt = Patient.objects.create(
            first_name="Juggie",
            last_name="Brodeltein",
            middle_name="Bayer",
            phone='+49 178 236 5288',
            gender=Gender.objects.first(),
            address='Schulstrasse 9',
            city='Munich',
            state='BA',
            zip_code='63108',
            pcp_preferred_zip='63018',
            date_of_birth=datetime.date(1990, 01, 01),
            patient_comfortable_with_english=False,
            preferred_contact_method=self.contact_method,
        )

    def test_select_referral_type_urls(self):
        '''
        Verify that all the referral creation URLs are accessible.
        '''
        # Create two different referral types
        reftype1 = ReferralType.objects.create(
            name="Specialty", is_fqhc=False)
        reftype2 = ReferralType.objects.create(
            name="FQHC", is_fqhc=True)

        # Check that select referral view
        url = reverse("select-referral-type",
                      args=(self.pt.id,))
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)
        self.assertContains(response, 'href="%s"' % reverse("new-referral",
                            args=(self.pt.id, reftype1.slugify(),)))
        self.assertContains(response, 'href="%s"' % reverse("new-referral",
                            args=(self.pt.id, reftype2.slugify(),)))


class TestCreateReferral(TestCase):
    '''
    Tests the create referral page
    '''
    fixtures = ['pttrack']

    def setUp(self):
        from pttrack.test_views import log_in_provider, build_provider
        log_in_provider(self.client, build_provider())

        self.contact_method = ContactMethod.objects.create(
            name="Carrier Pidgeon")

        self.pt = Patient.objects.create(
            first_name="Juggie",
            last_name="Brodeltein",
            middle_name="Bayer",
            phone='+49 178 236 5288',
            gender=Gender.objects.first(),
            address='Schulstrasse 9',
            city='Munich',
            state='BA',
            zip_code='63108',
            pcp_preferred_zip='63018',
            date_of_birth=datetime.date(1990, 01, 01),
            patient_comfortable_with_english=False,
            preferred_contact_method=self.contact_method,
        )

    def test_location_list(self):
        '''
        Verifies that the location list corresponding
        to a referral type are displayed
        '''
        # Create two different referral types
        specialty = ReferralType.objects.create(
            name="Specialty", is_fqhc=False)
        fqhc = ReferralType.objects.create(
            name="FQHC", is_fqhc=True)

        coh = ReferralLocation.objects.create(
            name='COH', address='Euclid Ave.')
        podiatrist = ReferralLocation.objects.create(
            name='Podiatry', address='Euclid Ave.')
        fqhc1 = ReferralLocation.objects.create(
            name='FQHC1', address='Euclid Ave.')
        fqhc2 = ReferralLocation.objects.create(
            name='FQHC2', address='Euclid Ave.')

        coh.care_availiable.add(specialty)
        podiatrist.care_availiable.add(specialty)
        fqhc1.care_availiable.add(fqhc)
        fqhc2.care_availiable.add(fqhc)

        # Check if both FQHCs options are included if FQHC type is selected
        url = reverse('new-referral',
                      args=(self.pt.id, fqhc.slugify(),))
        response = self.client.get(url)

        self.assertEquals(response.status_code, 200)
        self.assertContains(response, fqhc1.name)
        self.assertContains(response, fqhc2.name)

        # Check if both Specialty referral options are on specialty referral page
        url = reverse('new-referral',
                      args=(self.pt.id, specialty.slugify(),))
        response = self.client.get(url)

        self.assertEquals(response.status_code, 200)
        self.assertContains(response, coh.name)
        self.assertContains(response, podiatrist.name)

class TestSelectReferral(TestCase):

    fixtures = ['pttrack']

    def setUp(self):
        from pttrack.test_views import log_in_provider, build_provider
        log_in_provider(self.client, build_provider())

        self.contact_method = ContactMethod.objects.create(
            name="Carrier Pidgeon")

        self.pt = Patient.objects.create(
            first_name="Juggie",
            last_name="Brodeltein",
            middle_name="Bayer",
            phone='+49 178 236 5288',
            gender=Gender.objects.first(),
            address='Schulstrasse 9',
            city='Munich',
            state='BA',
            zip_code='63108',
            pcp_preferred_zip='63018',
            date_of_birth=datetime.date(1990, 01, 01),
            patient_comfortable_with_english=False,
            preferred_contact_method=self.contact_method,
        )

        self.reftype = ReferralType.objects.create(
            name="Specialty", is_fqhc=False)
        self.refloc = ReferralLocation.objects.create(
            name='COH', address='Euclid Ave.')
        self.refloc.care_availiable.add(self.reftype)


    def test_referral_list(self):
        '''
        Creates referrals and verifies that only appropriate ones are available
        in the select referral form
        '''
        # Create pending referral with follow up request
        referral1 = models.Referral.objects.create(
            comments="Needs his back checked",
            status='P',
            kind=self.reftype,
            author=Provider.objects.first(),
            author_type=ProviderType.objects.first(),
            patient=self.pt
        )
        referral1.location.add(self.refloc)

        followupRequest1 = models.FollowupRequest.objects.create(
            referral=referral1,
            contact_instructions="Call him",
            due_date=datetime.date(2018, 11, 01),
            author=Provider.objects.first(),
            author_type=ProviderType.objects.first(),
            patient=self.pt
        )

        # Create pending referral without a follow up request
        reftype2 = ReferralType.objects.create(
            name="FQHC", is_fqhc=True)
        refloc2 = ReferralLocation.objects.create(
            name='Family Health Center', address='Euclid Ave.')
        refloc2.care_availiable.add(reftype2)
        referral2 = models.Referral.objects.create(
            comments="Needs his back checked",
            status='P',
            kind=reftype2,
            author=Provider.objects.first(),
            author_type=ProviderType.objects.first(),
            patient=self.pt
        )
        referral2.location.add(refloc2)

        # Create a referral for a different patient
        pt2 = Patient.objects.create(
            first_name="Arthur",
            last_name="Miller",
            middle_name="",
            phone='+49 178 236 5288',
            gender=Gender.objects.first(),
            address='Schulstrasse 9',
            city='Munich',
            state='BA',
            zip_code='63108',
            pcp_preferred_zip='63018',
            date_of_birth=datetime.date(1994, 01, 22),
            patient_comfortable_with_english=False,
            preferred_contact_method=self.contact_method,
        )

        reftype3 = ReferralType.objects.create(
            name="Dentist", is_fqhc=False)
        refloc3 = ReferralLocation.objects.create(
            name='Family Dental', address='Euclid Ave.')
        refloc3.care_availiable.add(reftype3)

        referral3 = models.Referral.objects.create(
            comments="Needs his back checked",
            status='P',
            kind=reftype3,
            author=Provider.objects.first(),
            author_type=ProviderType.objects.first(),
            patient=pt2
        )
        referral3.location.add(refloc2)

        followupRequest2 = models.FollowupRequest.objects.create(
            referral=referral3,
            contact_instructions="Call him",
            due_date=datetime.date(2018, 11, 01),
            author=Provider.objects.first(),
            author_type=ProviderType.objects.first(),
            patient=pt2
        )

        # Verify that there is only one referral available for the first patient
        url = reverse('select-referral',
                      args=(self.pt.id,))
        response = self.client.get(url)

        self.assertEquals(response.status_code, 200)
        self.assertContains(response, referral1)
        self.assertNotContains(response, referral2)
        self.assertNotContains(response, referral3)

        # Verify that the appropriate referral is available for the second patient
        url = reverse('select-referral',
                      args=(pt2.id,))
        response = self.client.get(url)

        self.assertEquals(response.status_code, 200)
        self.assertNotContains(response, referral1)
        self.assertNotContains(response, referral2)
        self.assertContains(response, referral3)

        # Change the first referral's status to successful
        # No referrals should be available for patient 1
        referral1.status = models.Referral.STATUS_SUCCESSFUL
        referral1.save()

        url = reverse('select-referral',
                      args=(self.pt.id,))
        response = self.client.get(url)

        self.assertEquals(response.status_code, 200)
        self.assertNotContains(response, referral1)
        self.assertNotContains(response, referral2)
        self.assertNotContains(response, referral3)
