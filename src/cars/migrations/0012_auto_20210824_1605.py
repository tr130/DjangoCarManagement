# Generated by Django 3.2.6 on 2021-08-24 16:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cars', '0011_message'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='message',
            options={},
        ),
        migrations.AddField(
            model_name='partunit',
            name='total_cost',
            field=models.DecimalField(blank=True, decimal_places=2, default=0.0, max_digits=10),
            preserve_default=False,
        ),
    ]