from __future__ import print_function

from django.shortcuts import get_object_or_404, render
from django.utils.timezone import now
from django.core.urlresolvers import reverse
from django.views.generic.edit import FormView
from django.http import HttpResponseRedirect, HttpResponse
from .forms import FollowupRequestForm, ReferralForm, PatientContactForm, ReferralSelectForm
from pttrack.models import Patient, ProviderType
from .models import ReferralStatus, Referral, FollowupRequest, ReferralLocation


def select_referral_type(request, pt_id):
    '''Prompt the user to choose a referral type.'''
    pt = get_object_or_404(Patient, pk=pt_id)
    return render(request, 'referral/select-referral-type.html', {'pt': pt})


class ReferralCreate(FormView):
    template_name = 'referral/new-referral.html'
    form_class = ReferralForm

    def get_form_kwargs(self):
        kwargs = super(ReferralCreate, self).get_form_kwargs()

        print(self.kwargs)
        rtype = self.kwargs['rtype']
        if rtype == 'fqhc':
            kwargs['referral_location_qs'] = ReferralLocation.objects.filter(is_fqhc=True)
        elif rtype == 'specialty':
            kwargs['referral_location_qs'] = ReferralLocation.objects.filter(is_specialty=True)
        else:
            # FREAK OUT
            assert False

        return kwargs

    def get_context_data(self, **kwargs):
        context = super(ReferralCreate, self).get_context_data(**kwargs)

        # Add referral type to context data
        if 'rtype' in self.kwargs:
            context['rtype'] = self.kwargs['rtype']

        # Add patient to context data
        if 'pt_id' in self.kwargs:
            context['patient'] = Patient.objects.get(pk=self.kwargs['pt_id'])
        return context

    def form_valid(self, form):
        """Set the patient, provider, and written timestamp, and status."""
        pt = get_object_or_404(Patient, pk=self.kwargs['pt_id'])
        referral = form.save(commit=False)

        referral.completion_date = None
        referral.author = self.request.user.provider
        referral.author_type = get_object_or_404(
            ProviderType, pk=self.request.session['clintype_pk'])
        referral.patient = pt
        referral.status = ReferralStatus(name='P')

        referral.save()

        return HttpResponseRedirect(reverse('new-followup-request',
                                            args=(pt.id, referral.id,)))

# class SpecialtyReferralCreate(FormView):
#     template_name = 'referral/new-specialty-referral.html'
#     form_class = SpecialtyReferralForm

#     def get_context_data(self, **kwargs):
#         context = super(SpecialtyReferralCreate, self).get_context_data(**kwargs)

#         # Add patient to context data
#         if 'pt_id' in self.kwargs:
#             context['patient'] = Patient.objects.get(pk=self.kwargs['pt_id'])
#         return context

#     def form_valid(self, form):
#         """Set the patient, provider, and written timestamp, and status."""
#         pt = get_object_or_404(Patient, pk=self.kwargs['pt_id'])
#         referral = form.save(commit=False)

#         referral.completion_date = None
#         referral.author = self.request.user.provider
#         referral.author_type = get_object_or_404(
#             ProviderType, pk=self.request.session['clintype_pk'])
#         referral.patient = pt
#         referral.referral_status = ReferralStatus(name='P')

#         referral.save()

#         return HttpResponseRedirect(reverse('new-followup-request',
#                                             args=(pt.id, referral.id,)))


# class FQHCReferralCreate(FormView):
#     template_name = 'referral/new-FQHC-referral.html'
#     form_class = FQHCReferralForm

#     def get_context_data(self, **kwargs):
#         context = super(FQHCReferralCreate, self).get_context_data(**kwargs)

#         # Add patient to context data
#         if 'pt_id' in self.kwargs:
#             context['patient'] = Patient.objects.get(pk=self.kwargs['pt_id'])
#         return context

#     def form_valid(self, form):
#         """Set the patient, provider, and written timestamp, and status."""
#         pt = get_object_or_404(Patient, pk=self.kwargs['pt_id'])
#         referral = form.save(commit=False)

#         referral.completion_date = None
#         referral.author = self.request.user.provider
#         referral.author_type = get_object_or_404(
#             ProviderType, pk=self.request.session['clintype_pk'])
#         referral.patient = pt
#         referral.referral_status = ReferralStatus(name='P')

#         referral.save()

#         return HttpResponseRedirect(reverse('new-followup-request',
#                                             args=(pt.id, referral.id,)))


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

        # @Artur, should probably add something about referral being complete

        # Fill in remaining fields of form
        patient_contact.author = self.request.user.provider
        patient_contact.author_type = get_object_or_404(
            ProviderType, pk=self.request.session['clintype_pk'])
        patient_contact.referral = referral
        patient_contact.patient = pt
        patient_contact.followupRequest = followup_request
        patient_contact.save()
        form.save_m2m()

        return HttpResponseRedirect(reverse('patient-detail', args=(pt.id,)))

def select_referral(request, pt_id):
    if request.method == 'POST':
        form = ReferralSelectForm(request.POST)
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
        form = ReferralSelectForm()
        form.fields['referrals'].queryset = Referral.objects.filter(patient_id=pt_id)
        return render(request, 'referral/select-referral.html', {'form': form})
