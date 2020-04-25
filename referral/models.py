"""Data models for referral system."""
from django.db import models
# from django.core.urlresolvers import reverse
from django.urls import reverse

from pttrack.models import (ReferralType, ReferralLocation, Note,
                            ContactMethod, CompletableMixin,)
from followup.models import ContactResult, NoAptReason, NoShowReason
from django.utils.translation import gettext as _


class Referral(Note):
    """A record of a particular patient's referral to a particular center."""

    STATUS_SUCCESSFUL = 'S'
    STATUS_PENDING = 'P'
    STATUS_UNSUCCESSFUL = 'U'

    # Status if there are no referrals of a specific type
    # Used in aggregate_referral_status
    NO_REFERRALS_CURRENTLY = _("No referrals currently")

    REFERRAL_STATUSES = (
        (STATUS_SUCCESSFUL, _('Successful')),
        (STATUS_PENDING, _('Pending')),
        (STATUS_UNSUCCESSFUL, _('Unsuccessful')),
    )

    location = models.ManyToManyField(ReferralLocation, verbose_name=_("location"))
    comments = models.TextField(blank=True, verbose_name=_("comments"))
    status = models.CharField(
        max_length=50, choices=REFERRAL_STATUSES, default=STATUS_PENDING)
    kind = models.ForeignKey(
        ReferralType,
        on_delete=models.CASCADE,
        help_text=_("The kind of care the patient should recieve at the referral location."))


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
            referral_status_output = Referral.NO_REFERRALS_CURRENTLY

        return referral_status_output


class FollowupRequest(Note, CompletableMixin):

    referral = models.ForeignKey(Referral)
    contact_instructions = models.TextField(verbose_name=_("Contact instructions"))

    MARK_DONE_URL_NAME = 'new-patient-contact'
    ADMIN_URL_NAME = ''

    def class_name(self):
        return self.__class__.__name__

    def short_name(self):
        return _("Referral")

    def summary(self):
        return self.contact_instructions

    def mark_done_url(self):
        return reverse(self.MARK_DONE_URL_NAME,
                       args=(self.referral.patient.id,
                             self.referral.id,
                             self.id))

    def admin_url(self):
        return reverse(
            'admin:referral_followuprequest_change',
            args=(self.id,)
        )

    def __unicode__(self):
        formatted_date = self.due_date.strftime("%D", verbose_name=_("Due date"))
        return 'Followup with %s on %s about %s' % (self.patient,
                                                    formatted_date,
                                                    self.referral)


class PatientContact(Note):

    followup_request = models.ForeignKey(FollowupRequest)
    referral = models.ForeignKey(Referral)

    contact_method = models.ForeignKey(
        ContactMethod,
        null=False,
        blank=False,
        help_text=_("What was the method of contact?"))

    contact_status = models.ForeignKey(
        ContactResult,
        blank=False,
        null=False,
        help_text=_("Did you make contact with the patient about this referral?"))

    PTSHOW_YES = "Y"
    PTSHOW_NO = "N"
    PTSHOW_OPTS = [(PTSHOW_YES, _("Yes")),
                   (PTSHOW_NO, _("No"))]

    has_appointment = models.CharField(
        choices=PTSHOW_OPTS,
        blank=True, max_length=1,
        verbose_name=_("Appointment scheduled?"),
        help_text=_("Did the patient make an appointment?"))

    no_apt_reason = models.ForeignKey(
        NoAptReason,
        blank=True,
        null=True,
        verbose_name=_("No appointment reason"),
        help_text=_("If the patient didn't make an appointment, why not?"))

    appointment_location = models.ManyToManyField(
        ReferralLocation,
        blank=True,
        help_text=_("Where did the patient make an appointment?"))

    pt_showed = models.CharField(
        max_length=1,
        choices=PTSHOW_OPTS,
        blank=True,
        null=True,
        verbose_name=_("Appointment attended?"),
        help_text=_("Did the patient show up to the appointment?"))

    no_show_reason = models.ForeignKey(
        NoShowReason,
        blank=True,
        null=True,
        help_text=_("If the patient didn't go to the appointment, why not?"))

    def short_text(self):
        """Return a short text description of this followup and what happened.

        Used on the patient chart view as the text in the list of followups.
        """

        text = ""
        locations = " ,".join(map(str, self.appointment_location.all()))
        if self.pt_showed == self.PTSHOW_YES:
            text = _("Patient went to appointment at ") + locations + "."
        else:
            if self.has_appointment == self.PTSHOW_YES:
                text = (_("Patient made appointment at ") + locations +
                       _("but has not yet gone."))
            else:
                if self.contact_status.patient_reached:
                    text = _("Successfully contacted patient but the patient has not made an appointment yet.")
                else:
                    text = _("Did not successfully contact patient")
        return text
