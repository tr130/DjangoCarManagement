# Generated by Django 3.2.6 on 2021-08-09 11:39

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cars', '0004_labourunit_consumables'),
    ]

    operations = [
        migrations.AddField(
            model_name='job',
            name='estimated_time',
            field=models.DurationField(default=datetime.timedelta(0)),
        ),
    ]
