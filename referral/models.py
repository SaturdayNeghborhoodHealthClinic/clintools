"""Data models for referral system."""
from django.db import models
from pttrack.models import ReferralType, Note, Provider, ContactMethod, CompleteableManager, CompletableMixin
from followup.models import ContactResult, NoAptReason, NoShowReason

# pylint: disable=I0011,E1305

# class FollowupRequestManager(models.Manager):

#     def get_active(self, patient):
#         return sorted(
#             FollowupRequest.objects\
#                 .filter(patient=self.patient)\
#                 .exclude(completion_author=None),
#             key=lambda fu: fu.completion_date)

class ReferralLocation(models.Model):
    name = models.CharField(max_length=300)
    is_fqhc = models.NullBooleanField()
    is_specialty = models.NullBooleanField()

    def __unicode__(self):
        return self.name

class ReferralStatus(models.Model):
    REFERRAL_STATUS = (
        ('S', 'Successful'),
        ('P', 'Pending'),
        ('U', 'Unsuccessful'),
    )
    name = models.CharField(max_length=50, choices=REFERRAL_STATUS,
                            primary_key=True)

class Referral(Note):

    FQHC_REFERRAL = 'FQHC'
    SPECIALTY_REFERRAL = 'SPEC'

    REFERRAL_TYPES = (
        (FQHC_REFERRAL, 'Primary Care (FQHC)'),
        (SPECIALTY_REFERRAL, 'Specialty')
    )

    # Note I'm making this a Many to Many field for now since we'd like to be able to select 
    # multiple choices (maybe can be done on the front end only)
    location = models.ManyToManyField(ReferralLocation)
    comments = models.TextField(blank=True)
    status = models.ForeignKey(ReferralStatus)
    kind = models.CharField(max_length=10, choices=REFERRAL_TYPES)

    def __str__(self):
        formatted_date = self.written_datetime.strftime("%D")
        return "Referred to %s on %s" % (self.location, formatted_date)


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

    # Add question: Did patient attempt to contact FQHC to schedule appointment?

    # Add question: Which FQHC did the patient contact? 

    APPOINTMENT_HELP = "Did the patient make an appointment?"
    has_appointment = models.CharField(APPOINTMENT_HELP, choices=PTSHOW_OPTS,
                                       max_length=7)

    PTSHOW_HELP = "Did the patient show up to the appointment?"
    pt_showed = models.CharField(PTSHOW_HELP,
                                 max_length=7,
                                 choices=PTSHOW_OPTS,
                                 blank=True,
                                 null=True)

    NOAPT_HELP = "If the patient didn't make an appointment, why not?"
    no_apt_reason = models.ForeignKey(NoAptReason,
                                      verbose_name=NOAPT_HELP,
                                      blank=True,
                                      null=True)

    NOSHOW_HELP = "If the patient didn't go to appointment, why not?"
    no_show_reason = models.ForeignKey(NoShowReason,
                                       verbose_name=NOSHOW_HELP,
                                       blank=True,
                                       null=True)
