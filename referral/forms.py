from __future__ import print_function

from django.forms import ModelForm
from django import forms
from . import models
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Fieldset
from bootstrap3_datetime.widgets import DateTimePicker

# class ReferralForm(ModelForm):
#     class Meta:
#         model = models.Referral
#         exclude = ['patient', 'author',
#                    'author_type', 'written_datetime',
#                    'last_modified', 'referral_status']

#     def __init__(self, *args, **kwargs):
#         super(ReferralForm, self).__init__(*args, **kwargs)
#         self.helper = FormHelper(self)
#         self.helper.add_input(Submit('submit', 'Add referral followup'))

class ReferralForm(ModelForm):
    class Meta:
        model = models.Referral
        exclude = ['patient', 'author',
                   'author_type', 'written_datetime',
                   'last_modified', 'status', 'kind']

    def __init__(self, referral_location_qs, *args, **kwargs):
        super(ReferralForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper(self)

        # To future self, if we want FQHC referrals to have multiple choices 
        # BUT we want specialty referrals to only point to one location, then I think these need to be different forms
        self.fields['location'].widget = forms.widgets.CheckboxSelectMultiple()
        self.fields['location'].queryset = referral_location_qs
        self.helper.add_input(Submit('submit', 'Create referral'))

# class FQHCReferralForm(ModelForm):
#     class Meta:
#         model = models.FQHCReferral
#         exclude = ['patient', 'author',
#                    'author_type', 'written_datetime',
#                    'last_modified', 'referral_status', 'kind']

#     def __init__(self, *args, **kwargs):
#         super(FQHCReferralForm, self).__init__(*args, **kwargs)
#         self.helper = FormHelper(self)
#         self.fields['location'].queryset = models.ReferralLocation.objects.filter(is_FQHC=True)
#         self.helper.add_input(Submit('submit', 'Add referral followup'))

class FollowupRequestForm(ModelForm):
    class Meta:
        model = models.FollowupRequest
        exclude = ['patient', 'author',
                   'author_type', 'written_datetime',
                   'last_modified', 'completion_date',
                   'completion_author', 'referral']
        widgets = {'due_date': DateTimePicker(options={"format": "YYYY-MM-DD",
                                                       "pickTime": False})}

    def __init__(self, *args, **kwargs):
        super(FollowupRequestForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.add_input(Submit('submit', 'Submit'))

class PatientContactForm(ModelForm):
    class Meta:
        model = models.PatientContact
        exclude = ['referral', 'followupRequest', 'patient',
                   'author', 'author_type']

    def __init__(self, referral_location_qs, *args, **kwargs):
        super(PatientContactForm, self).__init__(*args, **kwargs)
        self.fields['appointment_location'].queryset = referral_location_qs
        self.helper = FormHelper(self)
        self.helper.add_input(Submit('successful-referral',
                                     'Successful referral'))
        self.helper.add_input(Submit('request-new-followup',
                                     'Request new followup'))
        self.helper.add_input(Submit('give-up',
                                     'Close referral - patient lost to followup'))

    def clean(self):
        '''Form has some complicated logic around which parts of the form can 
        be left blank and which ones must be filled out. 
        We check for a valid form submission here.'''

        cleaned_data = super(PatientContactForm, self).clean()

        # Break out of the method if the form has errors already
        # That is, certain required form elements are not filled in
        if self.errors:
            return

        has_appointment = cleaned_data.get("has_appointment")
        contact_status = cleaned_data.get("contact_status")

        patient_reached = contact_status.patient_reached

        if patient_reached:
            if has_appointment == "Yes":
                # Require user to specify if patient showed up for appointment
                # if that patient made an appointment
                if not cleaned_data.get("pt_showed"):
                    self.add_error(
                        "pt_showed", "Please specify whether the patient has" +
                        " gone to their appointment.")

                if not cleaned_data.get("appointment_location"):
                    self.add_error(
                        "appointment_location", "Please specify which " +
                        "provider the patient contacted.")

                if cleaned_data.get("no_apt_reason"):
                    self.add_error(
                        "no_apt_reason",
                        "If the patient has an appointment, a no " +
                        "appointment reason should not be given")

                pt_went = cleaned_data.get("pt_showed")
                if pt_went == "No":
                    if not cleaned_data.get("no_show_reason"):
                        self.add_error(
                            "no_show_reason", "Why didn't the patient go " +
                            "to the appointment?")

                if pt_went == "Yes":
                    if cleaned_data.get('no_show_reason'):
                        self.add_error(
                            "no_show_reason",
                            "If the patient showed, a no show reason should " +
                            "not be given.")
            elif has_appointment == "No" or has_appointment == "Not yet":
                # Require user to specify why the patient did not make
                # an appointment
                if not cleaned_data.get("no_apt_reason"):
                    self.add_error(
                        "no_apt_reason", "Why didn't the patient make " +
                        "an appointment?")
            else:
                if not cleaned_data.get("has_appointment"):
                    self.add_error(
                        "has_appointment", "Need to specify if patient " +
                        "has appointment")

        else:
            # If user did not make contact with the patient all other
            # parts of the form should be left blank
            detail_params = {
                "no_show_reason": "no show reason",
                "no_apt_reason": "no appointment reason",
                "pt_showed": "patient showed",
                "has_appointment": "has appointment"}

            for param, param_verbose in detail_params.iteritems():
                if cleaned_data.get(param):
                    self.add_error(
                        param,
                        "You can't give a " + param_verbose +
                        " value if contact was unsuccessful")

        # Each submission button has specific rules for which fields can be selected
        # For example, for a referral to be successful, the pt_went must be true
        pt_went = cleaned_data.get("pt_showed")
        if 'successful-referral' in self.data:
            if pt_went != "Yes":
                self.add_error(
                    "pt_showed", "Cannot submit a successful " +
                    "referral if the patient did not show up for" +
                    " an appointment")

        # Verify that give up is only selected if the patient has not
        # completed a referral
        if 'give-up' in self.data:
            if pt_went == "Yes":
                self.add_error(
                    "pt_showed", "Cannot give up on a " +
                    "successful referral")

        # Verify that give up is only selected if the patient has not
        # completed a referral
        if 'request-new-followup' in self.data:
            if pt_went == "Yes":
                self.add_error(
                    "pt_showed", "Cannot request a new referral " +
                    "follow up on a successful referral")


class ReferralSelectForm(forms.Form):
    referrals = forms.ModelChoiceField(queryset=models.Referral.objects.all())

    def __init__(self, *args, **kwargs):
        super(ReferralSelectForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.add_input(Submit('submit', 'Submit'))