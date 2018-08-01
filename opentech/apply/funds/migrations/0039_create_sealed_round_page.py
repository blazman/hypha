# Generated by Django 2.0.2 on 2018-08-01 16:08

import datetime
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import modelcluster.fields
import opentech.apply.stream_forms.models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('wagtailcore', '0040_page_draft_title'),
        ('funds', '0038_round_sealed'),
    ]

    operations = [
        migrations.CreateModel(
            name='SealedRound',
            fields=[
                ('page_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='wagtailcore.Page')),
                ('workflow_name', models.CharField(choices=[('single', 'Request'), ('double', 'Concept & Proposal')], default='single', max_length=100, verbose_name='Workflow')),
                ('start_date', models.DateField(default=datetime.date.today)),
                ('end_date', models.DateField(blank=True, default=datetime.date.today, help_text='When no end date is provided the round will remain open indefinitely.', null=True)),
                ('sealed', models.BooleanField(default=False)),
                ('lead', models.ForeignKey(limit_choices_to={'groups__name': 'Staff'}, on_delete=django.db.models.deletion.PROTECT, related_name='sealedround_lead', to=settings.AUTH_USER_MODEL)),
                ('reviewers', modelcluster.fields.ParentalManyToManyField(blank=True, limit_choices_to={'groups__name': 'Reviewer'}, related_name='sealedround_reviewer', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
            bases=(opentech.apply.stream_forms.models.BaseStreamForm, 'wagtailcore.page', models.Model),
        ),
        migrations.AlterField(
            model_name='round',
            name='reviewers',
            field=modelcluster.fields.ParentalManyToManyField(blank=True, limit_choices_to={'groups__name': 'Reviewer'}, related_name='round_reviewer', to=settings.AUTH_USER_MODEL),
        ),
    ]
