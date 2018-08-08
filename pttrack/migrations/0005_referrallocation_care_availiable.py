# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pttrack', '0004_auto_20180213_1616'),
    ]

    operations = [
        migrations.AddField(
            model_name='referrallocation',
            name='care_availiable',
            field=models.ManyToManyField(to='pttrack.ReferralType'),
        ),
    ]
