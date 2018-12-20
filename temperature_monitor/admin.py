from django.contrib import admin

from .models import Sensor, TimePoint


class TimePointInline(admin.TabularInline):
    model = TimePoint


@admin.register(Sensor)
class SensorAdmin(admin.ModelAdmin):
    inlines = [TimePointInline]
    save_on_top = True
    list_display = [
        'location',
        'last_seen',
        'time_since_last_seen',
        'probe_temp',
        'sensor_temp',
        'humidity',
        'serial_number',
        'timepoints_count',
        'device_type',
        'probe_alert_min_celsius_unitless',
        'probe_alert_max_celsius_unitless',
        'sensor_alert_min_celsius_unitless',
        'sensor_alert_max_celsius_unitless',
        'humidity_alert_min_unitless',
        'humidity_alert_max_unitless',
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
