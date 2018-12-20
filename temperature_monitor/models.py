import datetime
import pytz

from django.conf import settings
from django.db import models

import humanize


def convert_c_to_f(temperature):
    return 9 * temperature / 5 + 32


class Sensor(models.Model):
    device_type = models.CharField(
        help_text='Sensor type.',
        max_length=15,
    )
    location = models.CharField(
        help_text='Name and/or location of sensor.',
        max_length=20,
    )
    serial_number = models.CharField(
        help_text='',
        max_length=30,
        unique=True,
    )

    def __str__(self):
        return self.location

    @property
    def humidity(self):
        return self.timepoints.latest().humidity

    @property
    def last_seen(self):
        return self.timepoints.latest().time

    @property
    def probe_temp(self):
        if getattr(settings, 'TEMPERATURE_MONITOR_UNIT', 'C') is 'F':
            return self.timepoints.latest().probe_farhenheit
        else:
            return self.timepoints.latest().probe_celsius

    @property
    def sensor_temp(self):
        if getattr(settings, 'TEMPERATURE_MONITOR_UNIT', 'C') is 'F':
            return self.timepoints.latest().sensor_farhenheit
        else:
            return self.timepoints.latest().sensor_celsius

    @property
    def time_since_last_seen(self):
        return self.timepoints.latest().time_since

    class Meta:
        ordering = ['location']


class TimePoint(models.Model):
    sensor = models.ForeignKey(
        'Sensor',
        help_text='Sensor that collected this record.',
        related_name='timepoints',
        on_delete=models.PROTECT,
    )
    time = models.DateTimeField(
        help_text='Time data were collected.',
    )

    humidity_unitless = models.DecimalField(
        blank=True,
        decimal_places=1,
        help_text='Sensor percent humidity '
            '(enter the number only, no units).',
        max_digits=4,
        null=True,
    )
    probe_celsius_unitless = models.DecimalField(
        blank=True,
        decimal_places=1,
        help_text='Probe termperature in Celsius '
            '(enter the number only, no units).',
        max_digits=4,
        null=True,
    )
    sensor_celsius_unitless = models.DecimalField(
        blank=True,
        decimal_places=1,
        help_text='Sensor termperature in Celsius '
            '(enter the number only, no units).',
        max_digits=4,
        null=True,
    )

    def __str__(self):
        return '[{}] {}'.format(self.time, self.sensor.location)

    @property
    def humidity(self):
        if self.humidity_unitless is None:
            return None
        else:
            return '{}%'.format(self.humidity_unitless)

    @property
    def probe_celsius(self):
        if self.probe_celsius_unitless is None:
            return None
        else:
            return '{} ºC'.format(self.probe_celsius_unitless)

    @property
    def probe_farhenheit(self):
        if self.probe_farhenheit_unitless is None:
            return None
        else:
            return '{} ºF'.format(self.probe_farhenheit_unitless)

    @property
    def probe_farhenheit_unitless(self):
        if self.probe_celsius_unitless is None:
            return None
        else:
            return round(convert_c_to_f(self.probe_celsius_unitless), 1)

    @property
    def sensor_celsius(self):
        if self.sensor_celsius_unitless is None:
            return None
        else:
            return '{} ºC'.format(self.sensor_celsius_unitless)

    @property
    def sensor_farhenheit(self):
        if self.sensor_farhenheit_unitless is None:
            return None
        else:
            return '{} ºF'.format(self.sensor_farhenheit_unitless)

    @property
    def sensor_farhenheit_unitless(self):
        if self.sensor_celsius_unitless is None:
            return None
        else:
            return round(convert_c_to_f(self.sensor_celsius_unitless), 1)

    @property
    def time_since(self):
        now = datetime.datetime.now(pytz.timezone(settings.TIME_ZONE))
        return humanize.naturaltime(now - self.time)

    class Meta:
        get_latest_by = ['time']
        ordering = ['-time', 'sensor']
        unique_together = ['sensor', 'time']
