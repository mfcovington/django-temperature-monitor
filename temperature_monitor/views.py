from django.shortcuts import render
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.views.generic import DetailView, ListView

from .models import Gateway, Query, Sensor


@login_required
@permission_required(
    'temperature_monitor.view_sensor', raise_exception=True)
def home(request):
    context = {
        'gateway_count': Gateway.objects.count(),
        'query_count': Query.objects.count(),
        'sensor_count': Sensor.objects.count(),
        'gateway_alert': True in [g.alert for g in Gateway.objects.all()],
        'query_alert': Query.objects.latest().alert,
        'sensor_alert': True in [s.alert for s in Sensor.objects.all()],
    }
    return render(request, 'temperature_monitor/home.html', context)


class GatewayDetail(PermissionRequiredMixin, DetailView):
    context_object_name = 'gateway'
    model = Gateway
    permission_denied_message = ('You do not have permission to view gateway '
        'details.')
    permission_required = 'temperature_monitor.view_gateway'
    template_name = 'temperature_monitor/sensor_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['sensor_list'] = Sensor.objects.filter(gateway=self.object)
        return context


class GatewayList(PermissionRequiredMixin, ListView):
    context_object_name = 'gateway_list'
    model = Gateway
    permission_denied_message = ('You do not have permission to view gateway '
        'lists.')
    permission_required = 'temperature_monitor.view_gateway'


class QueryList(PermissionRequiredMixin, ListView):
    context_object_name = 'query_list'
    model = Query
    permission_denied_message = ('You do not have permission to view query '
        'lists.')
    permission_required = 'temperature_monitor.view_query'


class SensorDetail(PermissionRequiredMixin, DetailView):
    context_object_name = 'sensor'
    model = Sensor
    permission_denied_message = ('You do not have permission to view sensor '
        'details.')
    permission_required = 'temperature_monitor.view_sensor'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        gateway_pk = self.request.GET.get('gateway_pk', None)
        if gateway_pk:
            context['gateway'] = Gateway.objects.get(pk=gateway_pk)
        return context


class SensorList(PermissionRequiredMixin, ListView):
    context_object_name = 'sensor_list'
    model = Sensor
    permission_denied_message = ('You do not have permission to view sensor '
        'lists.')
    permission_required = 'temperature_monitor.view_sensor'
