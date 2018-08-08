# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pttrack', '0005_referrallocation_care_availiable'),
        ('followup', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='FollowupRequest',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('written_datetime', models.DateTimeField(auto_now_add=True)),
                ('last_modified', models.DateTimeField(auto_now=True)),
                ('completion_date', models.DateTimeField(null=True, blank=True)),
                ('due_date', models.DateField(help_text=b'MM/DD/YYYY or YYYY-MM-DD')),
                ('contact_instructions', models.TextField()),
                ('author', models.ForeignKey(to='pttrack.Provider')),
                ('author_type', models.ForeignKey(to='pttrack.ProviderType')),
                ('completion_author', models.ForeignKey(related_name='referral_followuprequest_completed', blank=True, to='pttrack.Provider', null=True)),
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
                ('has_appointment', models.CharField(max_length=7, verbose_name=b'Did the patient make an appointment?', choices=[(b'Yes', b'Yes'), (b'No', b'No'), (b'Not yet', b'Not yet')])),
                ('pt_showed', models.CharField(blank=True, max_length=7, null=True, verbose_name=b'Did the patient show up to the appointment?', choices=[(b'Yes', b'Yes'), (b'No', b'No'), (b'Not yet', b'Not yet')])),
                ('author', models.ForeignKey(to='pttrack.Provider')),
                ('author_type', models.ForeignKey(to='pttrack.ProviderType')),
                ('contact_method', models.ForeignKey(verbose_name=b'What was the method of contact?', to='pttrack.ContactMethod')),
                ('contact_status', models.ForeignKey(verbose_name=b'Did you make contact with the patient about this referral?', to='followup.ContactResult')),
                ('followupRequest', models.ForeignKey(to='referral.FollowupRequest')),
                ('no_apt_reason', models.ForeignKey(verbose_name=b"If the patient didn't make an appointment, why not?", blank=True, to='followup.NoAptReason', null=True)),
                ('no_show_reason', models.ForeignKey(verbose_name=b"If the patient didn't go to appointment, why not?", blank=True, to='followup.NoShowReason', null=True)),
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
                ('comments', models.TextField(blank=True)),
                ('status', models.CharField(default=b'P', max_length=50, choices=[(b'S', b'Successful'), (b'P', b'Pending'), (b'U', b'Unsuccessful')])),
                ('author', models.ForeignKey(to='pttrack.Provider')),
                ('author_type', models.ForeignKey(to='pttrack.ProviderType')),
                ('kind', models.ForeignKey(help_text=b'The kind of care the patient should recieve at the referral location.', to='pttrack.ReferralType')),
                ('location', models.ManyToManyField(to='pttrack.ReferralLocation')),
                ('patient', models.ForeignKey(to='pttrack.Patient')),
            ],
            options={
                'abstract': False,
            },
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
