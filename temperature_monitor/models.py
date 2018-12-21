import datetime
import pytz

from django.conf import settings
from django.db import models

import humanize


def convert_c_to_f(temperature):
    if temperature is None:
        return None
    else:
        return 9 * temperature / 5 + 32


def pretty_range(alert_min, alert_max, alert_type='temperature'):
    unit = ''
    if alert_type == 'temperature':
        unit = getattr(settings, 'TEMPERATURE_MONITOR_UNIT', 'C')
        if unit is 'F':
            alert_min = convert_c_to_f(alert_min)
            alert_max = convert_c_to_f(alert_max)
        unit = ' °{}'.format(unit)
    elif alert_type == 'humidity':
        unit = '%'

    if alert_min is None and alert_max is None:
        return '-'
    elif alert_min is None:
        return '≤ {}{}'.format(alert_max, unit)
    elif alert_max is None:
        return '≥ {}{}'.format(alert_min, unit)
    else:
        return '{}{} to {}{}'.format(
            alert_min, unit, alert_max, unit)


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

    battery = models.CharField(
        blank=True,
        help_text='',
        max_length=5,
        null=True,
    )
    link = models.CharField(
        blank=True,
        help_text='',
        max_length=5,
        null=True,
    )

    humidity_alert_min_unitless = models.SmallIntegerField(
        blank=True,
        help_text='',
        null=True,
    )
    humidity_alert_max_unitless = models.SmallIntegerField(
        blank=True,
        help_text='',
        null=True,
    )
    probe_alert_min_celsius_unitless = models.SmallIntegerField(
        blank=True,
        help_text='',
        null=True,
    )
    probe_alert_max_celsius_unitless = models.SmallIntegerField(
        blank=True,
        help_text='',
        null=True,
    )
    sensor_alert_min_celsius_unitless = models.SmallIntegerField(
        blank=True,
        help_text='',
        null=True,
    )
    sensor_alert_max_celsius_unitless = models.SmallIntegerField(
        blank=True,
        help_text='',
        null=True,
    )

    def __str__(self):
        return self.location

    @property
    def humidity(self):
        return self.timepoints.latest().humidity

    @property
    def humidity_range(self):
        return pretty_range(
            self.humidity_alert_min_unitless,
            self.humidity_alert_max_unitless,
            alert_type='humidity')

    @property
    def last_seen(self):
        return self.timepoints.latest().time

    @property
    def probe_range(self):
        return pretty_range(
            self.probe_alert_min_celsius_unitless,
            self.probe_alert_max_celsius_unitless)

    @property
    def probe_temp(self):
        if getattr(settings, 'TEMPERATURE_MONITOR_UNIT', 'C') is 'F':
            return self.timepoints.latest().probe_farhenheit
        else:
            return self.timepoints.latest().probe_celsius

    @property
    def sensor_range(self):
        return pretty_range(
            self.sensor_alert_min_celsius_unitless,
            self.sensor_alert_max_celsius_unitless)

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
