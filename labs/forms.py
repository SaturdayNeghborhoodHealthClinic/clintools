from django.forms import (
	fields, ModelForm, ModelChoiceField, ModelMultipleChoiceField, DecimalField, RadioSelect,Form
)
from django.shortcuts import render, redirect, get_object_or_404
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Div, Row, HTML, Field
from crispy_forms.bootstrap import (
    InlineCheckboxes, AppendedText, PrependedText)
from pttrack.models import Patient
from . import models
from django.db.models import DateTimeField, ForeignKey
import django.db
import decimal


# Create a lab object to a patient without any measurements 
class LabCreationForm(ModelForm):
	class Meta:
		model = models.Lab
		exclude = ['patient','written_datetime']

	def __init__(self, *args, **kwargs):
		patient_obj = kwargs.pop('pt')
		patient_name = patient_obj.name()
		super(LabCreationForm, self).__init__(*args, **kwargs)
		self.helper = FormHelper()
		self.helper.form_method = 'post'
		
		self.helper.layout = Layout(
			Row(HTML('<h3>Lab</h3>'),
				HTML('<p>Patient name: %s </p>' %patient_name),
				Div('lab_type', css_class='col-sm-6')),

			Submit('choose-lab', 'Choose Lab', css_class='btn btn-success')
		)
		

# Fill in corresponding measurements in a lab object
class MeasurementsCreationForm(Form):
	def __init__(self, *args, **kwargs):
		self.qs_fields = kwargs.pop('qs_mt')
		self.new_lab = kwargs.pop('new_lab')

		# Should check if the lab is already filled with measurments
		# How to check?

		super(MeasurementsCreationForm, self).__init__(*args, **kwargs)

		pt = self.new_lab.patient

		pt_info = Row(HTML('<h3>Lab</h3>'),
				HTML('<p>Patient name: %s </p>' %pt.name()),
				HTML('<p>Lab type: %s </p>' %self.new_lab.lab_type))

		self.fieldsss = [pt_info]
		for measurement_type in self.qs_fields:
			str_name = measurement_type.short_name
			unit = measurement_type.unit
			self.fieldsss.append(Field(str_name))
			self.fieldsss[-1] = AppendedText(str_name,unit)

			value_qs=models.DiscreteResultType.objects.filter(measurement_type=measurement_type)
			if len(value_qs)==0:
				self.fields[str_name] = DecimalField()
			else:
				self.fields[str_name]=ModelChoiceField(queryset=value_qs)


		self.helper = FormHelper()
		self.helper.form_method = 'post'

		if len(self.fieldsss)==0:
			button = []
		else:
			button = [Submit('save-lab', 'Save Lab', css_class='btn btn-success')]

		self.helper.layout = Layout(
			*(self.fieldsss + button)
			)

	def save(self):
		for field in self.qs_fields:
			if type(self.cleaned_data[field.short_name])==decimal.Decimal:
				models.ContinuousMeasurement.objects.create(
					measurement_type = field,
					lab = self.new_lab,
					value = self.cleaned_data[field.short_name]
				)
			else:
				models.DiscreteMeasurement.objects.create(
					measurement_type = field,
					lab = self.new_lab,
					value = self.cleaned_data[field.short_name]
				)
