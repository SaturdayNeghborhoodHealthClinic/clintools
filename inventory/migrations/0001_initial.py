# -*- coding: utf-8 -*-
# Generated by Django 1.11.28 on 2020-05-10 19:08
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='DrugCategory',
            fields=[
                ('name', models.CharField(max_length=100, primary_key=True, serialize=False)),
            ],
        ),
        migrations.CreateModel(
            name='Drugs',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('total_inventory', models.IntegerField(blank=True, default=0, null=True)),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='inventory.DrugCategory')),
            ],
        ),
        migrations.CreateModel(
            name='Formulation',
            fields=[
                ('dose', models.CharField(blank=True, max_length=10, primary_key=True, serialize=False)),
            ],
        ),
        migrations.AddField(
            model_name='drugs',
            name='dose',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='inventory.Formulation'),
        ),
    ]