# Generated by Django 3.2.6 on 2021-08-26 10:22

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('cars', '0014_auto_20210825_1108'),
    ]

    operations = [
        migrations.AddField(
            model_name='invoice',
            name='created',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
    ]
