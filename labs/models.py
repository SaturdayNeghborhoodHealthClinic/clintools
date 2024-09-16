# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import datetime

from django.db import models
from django.utils import timezone
from pttrack.models import Patient

# type of lab panels
# e.g. BMP, A1c, CBC, etc.
class LabType(models.Model):
	name = models.CharField(max_length=30, primary_key=True)

	def __unicode__(self):
		return self.name


# object of a lab panel
class Lab(models.Model):
	patient = models.ForeignKey(Patient)
	
	written_datetime = models.DateTimeField(auto_now_add=True)

	lab_type = models.ForeignKey(LabType)

	def __unicode__(self):
		to_tz = timezone.get_default_timezone()
		str_time = self.written_datetime.astimezone(to_tz).strftime("%B-%d-%Y, %H:%M")
		return '%s | %s | %s ' %(str(self.patient),str(self.lab_type),str_time)


# type of measurements in a lab panel
# e.g. Na+, K+ in BMP, A1c in A1c, WBC in CBC, etc.
class MeasurementType(models.Model):
    long_name = models.CharField(max_length=30, primary_key=True)
    short_name = models.CharField(max_length=15)
    unit = models.CharField(max_length=15, blank=True)

    lab_type = models.ForeignKey(LabType)

    def __unicode__(self):
        return self.long_name


# parent class of measurements
class Measurement(models.Model):
	measurement_type = models.ForeignKey(MeasurementType)
	lab = models.ForeignKey(Lab)


# object of a continuous measurement
class ContinuousMeasurement(Measurement):
	value = models.DecimalField(max_digits=5, decimal_places=1,blank=True, null=True)

	def __unicode__(self):
		return '%s: %2g' %(self.measurement_type, self.value)


# type of discrete results
# e.g. Positive, Negative, Trace, etc.
class DiscreteResultType(models.Model):
	name = models.CharField(max_length=30, primary_key=True)
	measurement_type = models.ManyToManyField(MeasurementType)

	def __unicode__(self):
		return self.name


# object of a continuous measurement
class DiscreteMeasurement(Measurement):
	value = models.ForeignKey(DiscreteResultType)

	def __unicode__(self):
		value_name = DiscreteResultType.objects.get(pk=self.value)
		return '%s: %s' %(self.measurement_type, value_name.name)
