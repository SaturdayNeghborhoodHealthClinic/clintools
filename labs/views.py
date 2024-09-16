# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from pttrack.models import Patient

from django.shortcuts import render, redirect, get_object_or_404
from django.core.urlresolvers import reverse
from django.views.generic import ListView, DetailView, CreateView
from .models import *
from .forms import LabCreationForm, MeasurementsCreationForm

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Div, Row, HTML, Field
from crispy_forms.bootstrap import (
	InlineCheckboxes, AppendedText, PrependedText)


class LabListView(ListView):
	model = Lab
	template_name = 'labs/lab_all.html'
	context_object_name = 'labs'
	ordering = ['-written_datetime']

	def get_queryset(self):
		self.pt = get_object_or_404(Patient, pk=self.kwargs['pt_id'])
		return Lab.objects.filter(patient=self.kwargs['pt_id'])


class LabDetailView(DetailView):
	model = Lab
	context_object_name = 'lab'

	def get_context_data(self, **kwargs):
		context = super(LabDetailView,self).get_context_data(**kwargs)
		self.lab = get_object_or_404(Lab, pk=self.kwargs['pk'])
		context['cont_list'] = ContinuousMeasurement.objects.filter(lab=self.lab)
		context['disc_list'] = DiscreteMeasurement.objects.filter(lab=self.lab)
		return context


def lab_create(request, pt_id):
	pt = get_object_or_404(Patient, pk=pt_id)

	if request.method == 'POST':
		form = LabCreationForm(request.POST,pt=pt)
		if form.is_valid():
			new_lab = form.save(commit=False)
			new_lab.patient = pt
			new_lab.save()
			return redirect(reverse("new-full-lab", args=(new_lab.pk,)))
	else:
		form = LabCreationForm(pt=pt)

	return render(request, 'labs/lab_create.html', {'form':form})


def full_lab_create(request, lab_id):
	lab = get_object_or_404(Lab, pk=lab_id)

	lab_type = lab.lab_type
	qs_mt = MeasurementType.objects.filter(lab_type=lab_type)

	if request.method == 'POST':
		form = MeasurementsCreationForm(request.POST,qs_mt=qs_mt, new_lab=lab)

		if form.is_valid():
			form.save()
			return redirect(reverse("lab-detail", args=(lab.pk,)))

	else:
		form = MeasurementsCreationForm(qs_mt=qs_mt, new_lab=lab)
	
	return render(request, 'labs/lab_create.html', {'form':form})
