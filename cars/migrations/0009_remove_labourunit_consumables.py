# Generated by Django 3.2.6 on 2021-08-10 13:33

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cars', '0008_auto_20210810_1216'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='labourunit',
            name='consumables',
        ),
    ]
