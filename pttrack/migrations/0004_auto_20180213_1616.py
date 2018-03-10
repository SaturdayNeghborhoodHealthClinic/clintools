# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pttrack', '0003_auto_20171014_1843'),
    ]

    operations = [
        migrations.AlterField(
            model_name='actionitem',
            name='completion_author',
            field=models.ForeignKey(related_name='pttrack_actionitem_completed', blank=True, to='pttrack.Provider', null=True),
        ),
    ]
