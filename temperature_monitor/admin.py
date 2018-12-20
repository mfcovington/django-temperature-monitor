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
        'serial_number',
        'timepoints_count',
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
