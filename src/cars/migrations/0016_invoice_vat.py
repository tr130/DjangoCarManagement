# Generated by Django 3.2.6 on 2021-08-26 10:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cars', '0015_invoice_created'),
    ]

    operations = [
        migrations.AddField(
            model_name='invoice',
            name='vat',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10),
        ),
    ]