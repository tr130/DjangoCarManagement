# Generated by Django 3.2.6 on 2021-09-01 15:46

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('parts', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='PartsOrder',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('placed', models.DateTimeField(auto_now_add=True)),
                ('sub_total', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('vat', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('grand_total', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('editable', models.BooleanField(default=True)),
            ],
        ),
        migrations.CreateModel(
            name='PartsOrderUnit',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.IntegerField()),
                ('cost_each', models.DecimalField(decimal_places=2, max_digits=10)),
                ('total_cost', models.DecimalField(decimal_places=2, max_digits=10)),
                ('checked_in', models.BooleanField(default=False)),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='parts.partsorder')),
                ('part', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='parts.part')),
            ],
        ),
    ]
