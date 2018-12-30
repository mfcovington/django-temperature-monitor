from django.contrib import admin

from .models import Gateway, Sensor, TimePoint


@admin.register(Gateway)
class GatewayAdmin(admin.ModelAdmin):
    list_display = [
        'serial_number',
        'last_seen',
        'time_since_last_seen',
        'sensors_count',
        '_timezone',
    ]

    def sensors_count(self, obj):
        return obj.sensors.count()
    sensors_count.short_description = '# of Sensors'


@admin.register(Sensor)
class SensorAdmin(admin.ModelAdmin):
    save_on_top = True
    list_display = [
        'location',
        'last_seen',
        'time_since_last_seen',
        'probe_temp',
        'probe_range',
        'battery',
        'link',
        'timepoints_count',
        'sensor_temp',
        'sensor_range',
        'humidity',
        'humidity_range',
        'device_type',
        'serial_number',
        'gateway',
    ]
    list_filter = [
        'gateway',
        'battery',
        'link',
    ]

    def timepoints_count(self, obj):
        return obj.timepoints.count()
    timepoints_count.short_description = '# of Timepoints'


@admin.register(TimePoint)
class TimePointAdmin(admin.ModelAdmin):
    fields = [
        'sensor',
        'time',
        'sensor_celsius_unitless',
        'probe_celsius_unitless',
        'humidity_unitless',
    ]
    list_display = [
        'time',
        'sensor',
        'probe_celsius',
        'probe_farhenheit',
        'sensor_celsius',
        'sensor_farhenheit',
        'humidity',
    ]
    list_filter = [
        'sensor__location',
    ]
    save_on_top = True
