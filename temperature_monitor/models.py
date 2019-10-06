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


class Gateway(models.Model):
    serial_number = models.CharField(
        help_text='',
        max_length=30,
        unique=True,
    )
    last_seen = models.DateTimeField(
        blank=True,
        help_text='Time gateway was last seen.',
        null=True,
    )
    _timezone = models.CharField(
        blank=True,
        help_text='Gateway\'s current time zone.',
        max_length=30,
        null=True,
    )

    def __str__(self):
        return self.serial_number

    @property
    def alert(self):
        return self.time_since_alert_a or self.time_since_alert_b

    @property
    def time_since_alert_a(self):
        return self.timedelta > datetime.timedelta(seconds=60*60*0.5)

    @property
    def time_since_alert_b(self):
        return self.timedelta > datetime.timedelta(seconds=60*60*3)

    @property
    def time_since_last_seen(self):
        return humanize.naturaltime(self.timedelta)

    @property
    def timedelta(self):
        now = datetime.datetime.now(pytz.timezone(self.timezone))
        if self.last_seen:
            return now - self.last_seen
        else:
            return None

    @property
    def timezone(self):
        if self._timezone:
            return self._timezone
        else:
            return settings.TIME_ZONE


class Query(models.Model):
    time = models.DateTimeField(
        blank=True,
        help_text='Time query started.',
        null=True,
        unique=True,
    )
    gateway_count = models.PositiveSmallIntegerField(
        default=0,
        help_text='Number of gateways queried.',
    )
    sensor_count = models.PositiveSmallIntegerField(
        default=0,
        help_text='Number of sensors queried.',
    )
    timepoint_count = models.PositiveSmallIntegerField(
        default=0,
        help_text='Number of timepoints queried.',
    )
    duration = models.DurationField(
        blank=True,
        help_text='Duration of query (seconds).',
        null=True,
    )

    def __str__(self):
        return str(self.time)

    @property
    def alert(self):
        return (self.gateway_alert or self.query_alert or self.sensor_alert
            or self.timepoint_alert)

    @property
    def gateway_alert(self):
        return self.gateway_count == 0

    @property
    def query_alert(self):
        return self.duration is None

    @property
    def sensor_alert(self):
        return self.sensor_count == 0

    @property
    def timedelta(self):
        now = datetime.datetime.now(pytz.timezone(settings.TIME_ZONE))
        return now - self.time

    @property
    def time_since(self):
        return humanize.naturaltime(self.timedelta)

    @property
    def timepoint_alert(self):
        return self.timepoint_count == 0

    class Meta:
        get_latest_by = ['time']
        ordering = ['-time']


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
    gateway = models.ForeignKey(
        'Gateway',
        blank=True,
        help_text='Gateway this sensor is connected to.',
        null=True,
        on_delete=models.SET_NULL,
        related_name='sensors',
    )

    battery = models.CharField(
        blank=True,
        help_text='',
        max_length=7,
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
    def alert(self):
        return self.alert_environment or self.alert_time

    @property
    def alert_environment(self):
        return self.humidity_alert or self.probe_alert or self.sensor_alert

    @property
    def alert_time(self):
        return self.time_since_alert_a or self.time_since_alert_b

    @property
    def humidity(self):
        return self.timepoints.latest().humidity

    @property
    def humidity_alert(self):
        try:
            humidity = self.timepoints.latest().humidity_unitless
        except:
            humidity = None
        low = float(self.humidity_alert_min_unitless or '-inf')
        high = float(self.humidity_alert_max_unitless or 'inf')
        if humidity and not low <= float(humidity) <= high:
            return True

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
    def probe_alert(self):
        try:
            temp = self.timepoints.latest().probe_celsius_unitless
        except:
            temp = None
        low = float(self.probe_alert_min_celsius_unitless or '-inf')
        high = float(self.probe_alert_max_celsius_unitless or 'inf')
        if temp and not low <= float(temp) <= high:
            return True

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
    def sensor_alert(self):
        try:
            temp = self.timepoints.latest().sensor_celsius_unitless
        except:
            temp = None
        low = float(self.sensor_alert_min_celsius_unitless or '-inf')
        high = float(self.sensor_alert_max_celsius_unitless or 'inf')
        if temp and not low <= float(temp) <= high:
            return True

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

    @property
    def time_since_alert_a(self):
        return self.timedelta > datetime.timedelta(seconds=60*60*3)

    @property
    def time_since_alert_b(self):
        return self.timedelta > datetime.timedelta(seconds=60*60*12)

    @property
    def timedelta(self):
        try:
            timedelta = self.timepoints.latest().timedelta
        except:
            timedelta = datetime.timedelta()
        return timedelta

    @property
    def timezone(self):
        if self.gateway and self.gateway.timezone:
            return self.gateway.timezone
        else:
            return settings.TIME_ZONE

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
        return humanize.naturaltime(self.timedelta)

    @property
    def timedelta(self):
        if self.sensor.timezone:
            timezone = self.sensor.timezone
        else:
            timezone = settings.TIME_ZONE
        now = datetime.datetime.now(pytz.timezone(timezone))
        if self.time:
            return now - self.time
        else:
            return None

    class Meta:
        get_latest_by = ['time']
        ordering = ['-time', 'sensor']
        unique_together = ['sensor', 'time']
