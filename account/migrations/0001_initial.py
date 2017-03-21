# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2016-12-12 02:31
from __future__ import unicode_literals

import account.models
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Account',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('birthDate', models.DateField(blank=True, null=True)),
                ('status', models.CharField(blank=True, choices=[('created', 'Created'), ('active', 'Active'), ('suspended', 'Suspended'), ('deleted', 'Deleted')], max_length=20)),
                ('gender', models.CharField(blank=True, max_length=30)),
                ('fullName', models.CharField(blank=True, max_length=150)),
                ('sexualOrientation', models.CharField(blank=True, choices=[('straight', 'Straight'), ('gay', 'Gay'), ('bisexual', 'Bisexual'), ('other', 'Other')], max_length=150)),
                ('sexualIdentity', models.CharField(blank=True, choices=[('woman', 'Woman'), ('man', 'Man'), ('other', 'Other')], max_length=150)),
                ('relationshipStatus', models.CharField(blank=True, choices=[('single', 'Single'), ('seeing_someone', 'Seeing someone'), ('married', 'Married'), ('open_relationship', 'Open relationship')], max_length=150)),
                ('relationshipType', models.CharField(blank=True, choices=[('monogamous', 'Monogamous'), ('non_monogamous', 'Non-monogamous')], max_length=150)),
                ('height', models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True)),
                ('bodyType', models.CharField(blank=True, choices=[('thin', 'Thin'), ('fit', 'Fit'), ('average_build', 'Average build'), ('a_little_extra', 'A little extra'), ('curvy', 'Curvy'), ('overweight', 'Overweight')], max_length=50)),
                ('ethnicity', models.CharField(blank=True, max_length=150)),
                ('languages', models.CharField(blank=True, max_length=150)),
                ('education', models.CharField(blank=True, max_length=150)),
                ('religion', models.CharField(blank=True, max_length=150)),
                ('vices', models.CharField(blank=True, max_length=150)),
                ('kids', models.CharField(blank=True, max_length=150)),
                ('diet', models.CharField(blank=True, max_length=150)),
                ('summary', models.TextField(blank=True, max_length=2000)),
                ('contactInfo', models.CharField(blank=True, max_length=150)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('user', models.OneToOneField(on_delete=models.SET(account.models.get_sentinel_user), to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
