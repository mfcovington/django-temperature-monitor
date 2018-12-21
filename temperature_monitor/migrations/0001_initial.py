# Generated by Django 2.1.4 on 2018-12-21 00:49

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Sensor',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('device_type', models.CharField(help_text='Sensor type.', max_length=15)),
                ('location', models.CharField(help_text='Name and/or location of sensor.', max_length=20)),
                ('serial_number', models.CharField(max_length=30, unique=True)),
                ('battery', models.CharField(blank=True, max_length=5, null=True)),
                ('link', models.CharField(blank=True, max_length=5, null=True)),
                ('humidity_alert_min_unitless', models.SmallIntegerField(blank=True, null=True)),
                ('humidity_alert_max_unitless', models.SmallIntegerField(blank=True, null=True)),
                ('probe_alert_min_celsius_unitless', models.SmallIntegerField(blank=True, null=True)),
                ('probe_alert_max_celsius_unitless', models.SmallIntegerField(blank=True, null=True)),
                ('sensor_alert_min_celsius_unitless', models.SmallIntegerField(blank=True, null=True)),
                ('sensor_alert_max_celsius_unitless', models.SmallIntegerField(blank=True, null=True)),
            ],
            options={
                'ordering': ['location'],
            },
        ),
        migrations.CreateModel(
            name='TimePoint',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('time', models.DateTimeField(help_text='Time data were collected.')),
                ('humidity_unitless', models.DecimalField(blank=True, decimal_places=1, help_text='Sensor percent humidity (enter the number only, no units).', max_digits=4, null=True)),
                ('probe_celsius_unitless', models.DecimalField(blank=True, decimal_places=1, help_text='Probe termperature in Celsius (enter the number only, no units).', max_digits=4, null=True)),
                ('sensor_celsius_unitless', models.DecimalField(blank=True, decimal_places=1, help_text='Sensor termperature in Celsius (enter the number only, no units).', max_digits=4, null=True)),
                ('sensor', models.ForeignKey(help_text='Sensor that collected this record.', on_delete=django.db.models.deletion.PROTECT, related_name='timepoints', to='temperature_monitor.Sensor')),
            ],
            options={
                'ordering': ['-time', 'sensor'],
                'get_latest_by': ['time'],
            },
        ),
        migrations.AlterUniqueTogether(
            name='timepoint',
            unique_together={('sensor', 'time')},
        ),
    ]
