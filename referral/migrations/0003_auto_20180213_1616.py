# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('referral', '0002_auto_20180116_2054'),
    ]

    operations = [
        migrations.RenameField(
            model_name='patientcontact',
            old_name='noapt_reason',
            new_name='no_apt_reason',
        ),
        migrations.RenameField(
            model_name='patientcontact',
            old_name='noshow_reason',
            new_name='no_show_reason',
        ),
        migrations.AlterField(
            model_name='followuprequest',
            name='completion_author',
            field=models.ForeignKey(related_name='referral_followuprequest_completed', blank=True, to='pttrack.Provider', null=True),
        ),
        migrations.AlterField(
            model_name='followuprequest',
            name='completion_date',
            field=models.DateTimeField(null=True, blank=True),
        ),
    ]
