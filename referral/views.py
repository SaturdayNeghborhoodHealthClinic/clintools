from __future__ import print_function
from django.utils.html import conditional_escape
from django.shortcuts import get_object_or_404, render
from django.utils.timezone import now
from django.core.urlresolvers import reverse
from django.views.generic.edit import FormView
from django.http import HttpResponseRedirect

from pttrack.models import Patient, ProviderType, ReferralType

from .models import Referral, FollowupRequest, ReferralLocation
from .forms import FollowupRequestForm, ReferralForm, PatientContactForm, ReferralSelectForm


def select_referral_type(request, pt_id):
    """Prompt the user to choose a referral type."""

    pt = get_object_or_404(Patient, pk=pt_id)

    extra_context = {
        'pt': pt,
        'referral_types': ReferralType.objects.all()}

    return render(
        request,
        'referral/select-referral-type.html',
        extra_context)


class ReferralSelect(FormView):
    template_name = ''
    form_class = ReferralSelectForm


class ReferralCreate(FormView):
    template_name = 'referral/new-referral.html'
    form_class = ReferralForm

    def get_form_kwargs(self):
        kwargs = super(ReferralCreate, self).get_form_kwargs()

        rtype_slug = self.kwargs['rtype']
        slugs = {referral_type.slugify(): referral_type for referral_type in ReferralType.objects.all()}
        rtype = slugs[rtype_slug]

        care_required = get_object_or_404(ReferralType, name=rtype)
        kwargs['referral_location_qs'] = ReferralLocation.objects.filter(
            care_availiable=care_required)

        return kwargs

    def get_context_data(self, **kwargs):
        context = super(ReferralCreate, self).get_context_data(**kwargs)

        # Add referral type to context data
        if 'rtype' in self.kwargs:
            rtype_slug = self.kwargs['rtype']
            slugs = {referral_type.slugify(): referral_type for referral_type in ReferralType.objects.all()}
            rtype = slugs[rtype_slug]
            context['rtype'] = rtype

        # # Add patient to context data
        if 'pt_id' in self.kwargs:
            context['patient'] = Patient.objects.get(pk=self.kwargs['pt_id'])

        return context

    def form_valid(self, form):
        """Set the patient, provider, and written timestamp, and status."""
        pt = get_object_or_404(Patient, pk=self.kwargs['pt_id'])
        referral = form.save(commit=False)

        # Get referral type from the URL
        rtype_slug = self.kwargs['rtype']
        slugs = {referral_type.slugify(): referral_type for referral_type in ReferralType.objects.all()}
        rtype = slugs[rtype_slug]
        referral.kind = get_object_or_404(ReferralType, name=rtype)

        # boilerplate for Note
        referral.author = self.request.user.provider
        referral.author_type = get_object_or_404(
            ProviderType, pk=self.request.session['clintype_pk'])
        referral.patient = pt

        referral.save()
        form.save_m2m()

        return HttpResponseRedirect(reverse('new-followup-request',
                                            args=(pt.id, referral.id,)))

class FollowupRequestCreate(FormView):
    """An explanation of the class."""

    template_name = 'referral/new-followup-request.html'
    form_class = FollowupRequestForm

    def get_context_data(self, **kwargs):
        context = super(FollowupRequestCreate, self).get_context_data(**kwargs)

        # Add patient to context data
        if 'pt_id' in self.kwargs:
            context['patient'] = Patient.objects.get(pk=self.kwargs['pt_id'])

        # Add referral information to context data
        if 'referral_id' in self.kwargs:
            context['referral'] = Referral.objects.get(
                pk=self.kwargs['referral_id'])

        return context

    def form_valid(self, form):
        pt = get_object_or_404(Patient, pk=self.kwargs['pt_id'])
        followup_request = form.save(commit=False)
        followup_request.completion_date = None
        followup_request.author = self.request.user.provider
        followup_request.author_type = get_object_or_404(
            ProviderType, pk=self.request.session['clintype_pk'])
        followup_request.referral = get_object_or_404(
            Referral, pk=self.kwargs['referral_id'])
        followup_request.patient = pt
        followup_request.save()
        return HttpResponseRedirect(reverse('patient-detail', args=(pt.id,)))


class PatientContactCreate(FormView):
    template_name = 'referral/new-patient-contact.html'
    form_class = PatientContactForm

    def get_form_kwargs(self):
        kwargs = super(PatientContactCreate, self).get_form_kwargs()
        # Add referral location queryset to kwargs
        referral = get_object_or_404(Referral, pk=self.kwargs['referral_id'])
        kwargs['referral_location_qs'] = referral.location.all()
        return kwargs

    def get_context_data(self, **kwargs):
        context = super(PatientContactCreate, self).get_context_data(**kwargs)

        # Add patient to context data
        if 'pt_id' in self.kwargs:
            context['patient'] = Patient.objects.get(pk=self.kwargs['pt_id'])

        # Add referral information to context data
        if 'referral_id' in self.kwargs:
            context['referral'] = Referral.objects.get(
                pk=self.kwargs['referral_id'])

        # Add follow up information to context data
        if 'followup_id' in self.kwargs:
            context['followup'] = FollowupRequest.objects.get(
                pk=self.kwargs['followup_id'])

        return context

    def form_valid(self, form):
        pt = get_object_or_404(Patient, pk=self.kwargs['pt_id'])
        referral = get_object_or_404(Referral, pk=self.kwargs['referral_id'])
        followup_request = get_object_or_404(FollowupRequest, pk=self.kwargs['followup_id'])

        # Add completion date to followup request
        followup_request.completion_date = now().date()
        followup_request.completion_author = self.request.user.provider
        followup_request.save()

        patient_contact = form.save(commit=False)

        # Fill in remaining fields of form
        patient_contact.author = self.request.user.provider
        patient_contact.author_type = get_object_or_404(
            ProviderType, pk=self.request.session['clintype_pk'])
        patient_contact.referral = referral
        patient_contact.patient = pt
        patient_contact.followup_request = followup_request
        patient_contact.save()
        form.save_m2m()

        # Redirect to appropriate page and update referral status
        if PatientContactForm.SUCCESSFUL_REFERRAL in self.request.POST:
            referral.status = Referral.STATUS_SUCCESSFUL
            referral.save()
            return HttpResponseRedirect(reverse('patient-detail', args=(pt.id,)))

        elif PatientContactForm.REQUEST_FOLLOWUP in self.request.POST:
            referral.status = Referral.STATUS_PENDING
            referral.save()
            return HttpResponseRedirect(reverse('new-followup-request',
                                                args=(pt.id, referral.id,)))
        elif PatientContactForm.UNSUCCESSFUL_REFERRAL in self.request.POST:
            referral.status = Referral.STATUS_UNSUCCESSFUL
            referral.save()
            return HttpResponseRedirect(reverse('patient-detail', args=(pt.id,)))

def select_referral(request, pt_id):
    if request.method == 'POST':
        form = ReferralSelectForm(pt_id, request.POST)
        if form.is_valid():
            # Get referral ID from form
            referral = form.cleaned_data['referrals']
            # Go to last followup request (note there should only ever be one open followup request)
            followup_requests = FollowupRequest.objects.filter(patient_id=pt_id,
                                                               referral=referral.id)
            followup_request = followup_requests.latest('id')
            return HttpResponseRedirect(reverse('new-patient-contact',
                                                args=(pt_id, referral.id,
                                                      followup_request.id)))
    else:
        form = ReferralSelectForm(pt_id)
        # Select active referrals
        # form.fields['referrals'].queryset = Referral.objects.filter(patient_id=pt_id,
        #                                                             status=Referral.STATUS_PENDING,
        #                                                             followuprequest__in=FollowupRequest.objects.all())
        return render(request, 'referral/select-referral.html', {'form': form})
