# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pttrack', '0003_auto_20171014_1843'),
        ('followup', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='FollowupRequest',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('written_datetime', models.DateTimeField(auto_now_add=True)),
                ('last_modified', models.DateTimeField(auto_now=True)),
                ('due_date', models.DateField(help_text=b'MM/DD/YYYY or YYYY-MM-DD')),
                ('contact_instructions', models.TextField()),
                ('completion_date', models.DateField(null=True, blank=True)),
                ('author', models.ForeignKey(to='pttrack.Provider')),
                ('author_type', models.ForeignKey(to='pttrack.ProviderType')),
                ('completion_author', models.ForeignKey(related_name='referral_followup_completed', blank=True, to='pttrack.Provider', null=True)),
                ('patient', models.ForeignKey(to='pttrack.Patient')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='PatientContact',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('written_datetime', models.DateTimeField(auto_now_add=True)),
                ('last_modified', models.DateTimeField(auto_now=True)),
                ('has_appointment', models.BooleanField(help_text=b'Did the patient make an appointment?')),
                ('pt_showed', models.CharField(blank=True, max_length=7, null=True, help_text=b'Did the patient show up to the appointment?', choices=[(b'Yes', b'Yes'), (b'No', b'No'), (b'Not yet', b'Not yet')])),
                ('author', models.ForeignKey(to='pttrack.Provider')),
                ('author_type', models.ForeignKey(to='pttrack.ProviderType')),
                ('contact_method', models.ForeignKey(to='pttrack.ContactMethod')),
                ('contact_status', models.ForeignKey(to='followup.ContactResult')),
                ('followupRequest', models.ForeignKey(to='referral.FollowupRequest')),
                ('noapt_reason', models.ForeignKey(blank=True, to='followup.NoAptReason', help_text=b"If the patient didn't make an appointment, why not?", null=True)),
                ('noshow_reason', models.ForeignKey(blank=True, to='followup.NoShowReason', help_text=b"If the patient didn't go to appointment, why not?", null=True)),
                ('patient', models.ForeignKey(to='pttrack.Patient')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Referral',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('written_datetime', models.DateTimeField(auto_now_add=True)),
                ('last_modified', models.DateTimeField(auto_now=True)),
                ('comments', models.TextField()),
                ('author', models.ForeignKey(to='pttrack.Provider')),
                ('author_type', models.ForeignKey(to='pttrack.ProviderType')),
                ('location', models.ForeignKey(to='pttrack.ReferralLocation', blank=True)),
                ('patient', models.ForeignKey(to='pttrack.Patient')),
                ('referralType', models.ForeignKey(to='pttrack.ReferralType', blank=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='ReferralStatus',
            fields=[
                ('name', models.CharField(max_length=50, serialize=False, primary_key=True)),
            ],
        ),
        migrations.AddField(
            model_name='referral',
            name='referral_status',
            field=models.ForeignKey(to='referral.ReferralStatus'),
        ),
        migrations.AddField(
            model_name='patientcontact',
            name='referral',
            field=models.ForeignKey(to='referral.Referral'),
        ),
        migrations.AddField(
            model_name='followuprequest',
            name='referral',
            field=models.ForeignKey(to='referral.Referral'),
        ),
    ]
