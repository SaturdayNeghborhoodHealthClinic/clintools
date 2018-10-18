"""Data models for referral system."""
from django.db import models
from django.core.exceptions import ValidationError

from pttrack.models import (
    ReferralType, ReferralLocation, Note, ContactMethod, CompletableMixin,
    CompleteableManager)
from followup.models import ContactResult, NoAptReason, NoShowReason

# pylint: disable=I0011,E1305

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

    location = models.ManyToManyField(ReferralLocation)
    comments = models.TextField(blank=True)
    status = models.CharField(
        max_length=50, choices=REFERRAL_STATUSES, default=STATUS_PENDING)
    kind = models.ForeignKey(
        ReferralType,
        help_text="The kind of care the patient should recieve at the "
                  "referral location.")

    def __unicode__(self):
        """Provides string to display on front end for referral.

           For FQHC referrals, returns referral kind and date.
           For non-FQHC referrals, returns referral location and date.
        """

        formatted_date = self.written_datetime.strftime("%D")
        if self.kind.is_fqhc:
            return "%s referral on %s" % (self.kind, formatted_date)
        else:
            location_names = [loc.name for loc in self.location.all()]
            locations = " ,".join(location_names)
            return "Referral to %s on %s" % (locations, formatted_date)

    @staticmethod
    def aggregate_referral_status(referrals):
        referral_status_output = ""
        if referrals:
            all_successful = all(referral.status == Referral.STATUS_SUCCESSFUL
                                 for referral in referrals)
            if all_successful:
                referral_status_output = (dict(Referral.REFERRAL_STATUSES)
                                          [Referral.STATUS_SUCCESSFUL])
            else:
                # Determine referral status based on the last FQHC referral
                referral_status_output = (dict(Referral.REFERRAL_STATUSES)
                                          [referrals.last().status])
        else:
            referral_status_output = "No referrals currently"

        return referral_status_output

class FollowupRequest(Note, CompletableMixin):

    referral = models.ForeignKey(Referral)
    contact_instructions = models.TextField()

    objects = CompleteableManager()

    def class_name(self):
        return self.__class__.__name__


class PatientContact(Note):

    followup_request = models.ForeignKey(FollowupRequest)
    referral = models.ForeignKey(Referral)

    contact_method = models.ForeignKey(
        ContactMethod,
        null=False,
        blank=False,
        help_text="What was the method of contact?")

    contact_status = models.ForeignKey(
        ContactResult,
        blank=False,
        null=False,
        help_text="Did you make contact with the patient about this referral?")

    PTSHOW_YES = "Y"
    PTSHOW_NO = "N"
    PTSHOW_NOTYET = "?"
    PTSHOW_OPTS = [(PTSHOW_YES, "Yes"),
                   (PTSHOW_NO, "No"),
                   (PTSHOW_NOTYET, "Not yet")]

    has_appointment = models.CharField(
        choices=PTSHOW_OPTS,
        blank=True, max_length=1,
        verbose_name="Appointment scheduled?",
        help_text="Did the patient make an appointment?")

    no_apt_reason = models.ForeignKey(
        NoAptReason,
        blank=True,
        null=True,
        verbose_name="No appointment reason",
        help_text="If the patient didn't make an appointment, why not?")

    appointment_location = models.ManyToManyField(
        ReferralLocation,
        blank=True,
        help_text="Where did the patient make an appointment?")

    pt_showed = models.CharField(
        max_length=1,
        choices=PTSHOW_OPTS,
        blank=True,
        null=True,
        verbose_name="Appointment attended?",
        help_text="Did the patient show up to the appointment?")

    no_show_reason = models.ForeignKey(
        NoShowReason,
        blank=True,
        null=True,
        help_text="If the patient didn't go to the appointment, why not?")

    def short_text(self):
        """Return a short text description of this followup and what happened.

        Used on the patient chart view as the text in the list of followups.
        """

        text = ""
        locations = " ,".join(map(str, self.appointment_location.all()))
        if self.pt_showed == self.PTSHOW_YES:
            text = "Patient went to appointment at " + locations + "."
        else:
            if self.has_appointment == self.PTSHOW_YES:
                text = ("Patient made appointment at " + locations +
                        "but has not yet gone.")
            else:
                if self.contact_status.patient_reached:
                    text = ("Successfully contacted patient but the "
                            "patient has not made an appointment yet.")
                else:
                    text = "Did not successfully contact patient"
        return text
