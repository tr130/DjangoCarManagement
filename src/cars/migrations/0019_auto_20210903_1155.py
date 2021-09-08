# Generated by Django 3.2.6 on 2021-09-03 11:55

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('cars', '0018_partrequest'),
    ]

    operations = [
        migrations.AddField(
            model_name='partrequest',
            name='on_order',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='partrequest',
            name='requested',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
    ]