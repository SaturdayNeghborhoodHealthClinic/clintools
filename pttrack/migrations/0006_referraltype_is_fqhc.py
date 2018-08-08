# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pttrack', '0005_referrallocation_care_availiable'),
    ]

    operations = [
        migrations.AddField(
            model_name='referraltype',
            name='is_fqhc',
            field=models.BooleanField(default=False),
        ),
    ]
