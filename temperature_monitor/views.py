from django.shortcuts import render
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.views.generic import DetailView, ListView

from .models import Sensor


class SensorDetail(PermissionRequiredMixin, DetailView):
    context_object_name = 'sensor'
    model = Sensor
    permission_denied_message = ('You do not have permission to view sensor '
        'details.')
    permission_required = 'temperature_monitor.view_sensor'


class SensorList(PermissionRequiredMixin, ListView):
    context_object_name = 'sensor_list'
    model = Sensor
    permission_denied_message = ('You do not have permission to view sensor '
        'lists.')
    permission_required = 'temperature_monitor.view_sensor'
