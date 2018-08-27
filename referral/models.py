"""Data models for referral system."""
from django.db import models
from django.core.exceptions import ValidationError

from pttrack.models import (
    ReferralType, ReferralLocation, Note, ContactMethod, CompletableMixin,
    CompleteableManager)
from followup.models import ContactResult, NoAptReason, NoShowReason

# pylint: disable=I0011,E1305

# class FollowupRequestManager(models.Manager):

#     def get_active(self, patient):
#         return sorted(
#             FollowupRequest.objects\
#                 .filter(patient=self.patient)\
#                 .exclude(completion_author=None),
#             key=lambda fu: fu.completion_date)


class Referral(Note):
    """A record of a particular patient's referral to a particular center."""

    STATUS_SUCCESSFUL = 'S'
    STATUS_PENDING = 'P'
    STATUS_UNSUCCESSFUL = 'U'

    REFERRAL_STATUSES = (
        (STATUS_SUCCESSFUL, 'Completed'),
        (STATUS_PENDING, 'Not completed'),
        (STATUS_UNSUCCESSFUL, 'Unsuccessful referral'),
    )

    # Note I'm making this a Many to Many field for now since we'd
    # like to be able to select  multiple choices (maybe can be
    # done on the front end only)
    location = models.ManyToManyField(ReferralLocation)
    comments = models.TextField(blank=True)
    status = models.CharField(
        max_length=50, choices=REFERRAL_STATUSES, default=STATUS_PENDING)
    kind = models.ForeignKey(
        ReferralType,
        help_text="The kind of care the patient should recieve at the "
                  "referral location.")

    # Note def clean throws an error when trying to write to the database
    # I found this helpful: https://stackoverflow.com/questions/17505935/django-error-needs-to-have-a-value-for-field-before-this-many-to-many-rel

    # def clean(self):
    #     if self.kind not in self.location.care_availiable:
    #         raise ValidationError(
    #             "Referral location %s does not offer %s care." %
    #             (self.location, self.kind))

    # This also doesn't work for unknown reasons

    def __unicode__(self):
        formatted_date = self.written_datetime.strftime("%D")
        return "%s referral on %s" % (self.kind, formatted_date)


# class FQHCInfo(Referral):
#     referral = models.OneToOneField(Referral)
#     location = models.ManyToManyField(FQHCLocation)

#     def __str__(self):
#         formatted_date = self.written_datetime.strftime("%D")
#         return "Referred to %s on %s" % (self.FQHC_location, formatted_date)

# class SpecialtyReferral(Referral):
#     location = models.ForeignKey(ReferralLocation)

#     def __str__(self):
#         formatted_date = self.written_datetime.strftime("%D")
#         return "Referred to %s on %s" % (self.location, formatted_date)

class FollowupRequest(Note, CompletableMixin):

    referral = models.ForeignKey(Referral)
    contact_instructions = models.TextField()

    objects = CompleteableManager()

    def class_name(self):
        return self.__class__.__name__

class PatientContact(Note):

    followupRequest = models.ForeignKey(FollowupRequest)
    referral = models.ForeignKey(Referral)

    CONTACT_METHOD_HELP = "What was the method of contact?"
    contact_method = models.ForeignKey(ContactMethod,
                                       verbose_name=CONTACT_METHOD_HELP)

    CONTACT_STATUS_HELP = "Did you make contact with the patient about this referral?"
    contact_status = models.ForeignKey(ContactResult,
                                       verbose_name=CONTACT_STATUS_HELP)

    PTSHOW_OPTS = [("Yes", "Yes"),
                   ("No", "No"),
                   ("Not yet", "Not yet")]

    APPOINTMENT_HELP = "Did the patient make an appointment?"
    has_appointment = models.CharField(APPOINTMENT_HELP, choices=PTSHOW_OPTS,
                                       blank=True, max_length=7)

    NOAPT_HELP = "If the patient didn't make an appointment, why not?"
    no_apt_reason = models.ForeignKey(NoAptReason,
                                      verbose_name=NOAPT_HELP,
                                      blank=True,
                                      null=True)

    APPOINTMENT_LOCATION_HELP = "Where did the patient make an appointment?"
    #location_options = Referral.objects.get(pk=referral.id).location
    #print(location_options)
    appointment_location = models.ManyToManyField(ReferralLocation,
                                                  blank=True,
                                                  verbose_name=APPOINTMENT_LOCATION_HELP)
    #                                           choices=location_options)

    PTSHOW_HELP = "Did the patient show up to the appointment?"
    pt_showed = models.CharField(PTSHOW_HELP,
                                 max_length=7,
                                 choices=PTSHOW_OPTS,
                                 blank=True,
                                 null=True)

    NOSHOW_HELP = "If the patient didn't go to appointment, why not?"
    no_show_reason = models.ForeignKey(NoShowReason,
                                       verbose_name=NOSHOW_HELP,
                                       blank=True,
                                       null=True)
