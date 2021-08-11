# Generated by Django 3.2.6 on 2021-08-10 10:29

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cars', '0005_job_estimated_time'),
    ]

    operations = [
        migrations.AddField(
            model_name='job',
            name='time_spent',
            field=models.DurationField(default=datetime.timedelta(0)),
        ),
        migrations.AddField(
            model_name='labourunit',
            name='time_spent',
            field=models.DurationField(default=datetime.timedelta(0)),
        ),
    ]
