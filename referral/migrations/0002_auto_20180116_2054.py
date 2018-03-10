# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('referral', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='referral',
            old_name='referralType',
            new_name='referral_type',
        ),
        migrations.AlterField(
            model_name='referralstatus',
            name='name',
            field=models.CharField(max_length=50, serialize=False, primary_key=True, choices=[(b'S', b'Successful'), (b'P', b'Pending'), (b'U', b'Unsuccessful')]),
        ),
    ]
