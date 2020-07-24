# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2018-07-09 01:07
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pttrack', '0004_auto_20171016_1646'),
    ]

    operations = [
        migrations.AddField(
            model_name='historicalactionitem',
            name='history_change_reason',
            field=models.CharField(max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='historicaldocument',
            name='history_change_reason',
            field=models.CharField(max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='historicalpatient',
            name='history_change_reason',
            field=models.CharField(max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='historicalprovider',
            name='history_change_reason',
            field=models.CharField(max_length=100, null=True),
        ),
    ]
