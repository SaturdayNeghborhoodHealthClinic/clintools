# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pttrack', '0006_referraltype_is_fqhc'),
        ('referral', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='patientcontact',
            name='appointment_location',
            field=models.ManyToManyField(to='pttrack.ReferralLocation', verbose_name=b'Which provider did the patient contact for an appointment?', blank=True),
        ),
        migrations.AlterField(
            model_name='patientcontact',
            name='has_appointment',
            field=models.CharField(blank=True, max_length=7, verbose_name=b'Did the patient make an appointment?', choices=[(b'Yes', b'Yes'), (b'No', b'No'), (b'Not yet', b'Not yet')]),
        ),
        migrations.AlterField(
            model_name='referral',
            name='status',
            field=models.CharField(default=b'P', max_length=50, choices=[(b'S', b'Completed'), (b'P', b'Not completed'), (b'U', b'Unsuccessful referral')]),
        ),
    ]
