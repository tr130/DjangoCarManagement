# Generated by Django 3.2.6 on 2021-08-05 11:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cars', '0003_car_reg'),
    ]

    operations = [
        migrations.AddField(
            model_name='labourunit',
            name='consumables',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=10),
            preserve_default=False,
        ),
    ]
