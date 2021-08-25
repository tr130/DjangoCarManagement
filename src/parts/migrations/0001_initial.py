# Generated by Django 3.2.6 on 2021-08-03 16:00

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Part',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('cost_price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('customer_price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('stock_level', models.PositiveIntegerField()),
            ],
        ),
    ]