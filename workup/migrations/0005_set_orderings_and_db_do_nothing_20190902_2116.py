# -*- coding: utf-8 -*-
# Generated by Django 1.11.23 on 2019-09-03 02:16
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
import pttrack.validators


class Migration(migrations.Migration):

    dependencies = [
        ('workup', '0004_add_progressnote_signing_20190813_2018'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='clinictype',
            options={'ordering': ['name']},
        ),
        migrations.AlterModelOptions(
            name='diagnosistype',
            options={'ordering': ['name']},
        ),
        migrations.AlterField(
            model_name='historicalprogressnote',
            name='signer',
            field=models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='pttrack.Provider', validators=[pttrack.validators.validate_attending]),
        ),
        migrations.AlterField(
            model_name='historicalworkup',
            name='attending',
            field=models.ForeignKey(blank=True, db_constraint=False, help_text=b'Which attending saw the patient?', null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='pttrack.Provider', validators=[pttrack.validators.validate_attending]),
        ),
        migrations.AlterField(
            model_name='historicalworkup',
            name='clinic_day',
            field=models.ForeignKey(blank=True, db_constraint=False, help_text=b'When was the patient seen?', null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='workup.ClinicDate'),
        ),
        migrations.AlterField(
            model_name='historicalworkup',
            name='signer',
            field=models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='pttrack.Provider', validators=[pttrack.validators.validate_attending]),
        ),
    ]
