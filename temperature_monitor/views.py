from django.shortcuts import render
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views.generic import DetailView, ListView

from .models import Gateway, Query, Sensor
from .tasks import update as scrape_lacrosse


def latest_query():
    try:
        return Query.objects.latest()
    except:
        return None


@login_required
@permission_required(
    'temperature_monitor.view_sensor', raise_exception=True)
def home(request):
    try:
        query_alert = latest_query().alert
    except Exception as e:
        query_alert = None
    context = {
        'gateway_count': Gateway.objects.count(),
        'query_count': Query.objects.count(),
        'sensor_count': Sensor.objects.count(),
        'gateway_alert': True in [g.alert for g in Gateway.objects.all()],
        'query_alert': query_alert,
        'sensor_alert_environment': True in [
            s.alert_environment for s in Sensor.objects.all()],
        'sensor_alert_time': True in [
            s.alert_time for s in Sensor.objects.all()],
        'latest_query': latest_query(),
        'update_delay': 60 * getattr(
            settings, 'LA_CROSSE_ALERTS_UPDATE_DELAY', 5),
    }
    return render(request, 'temperature_monitor/home.html', context)


@login_required
@permission_required(
    'temperature_monitor.add_sensor', raise_exception=True)
def update(request):
    """
    Manually query La Crosse Alerts site.
    """
    try:
        scrape_lacrosse.delay()
        message = 'Update started (should complete within 30-60 seconds).'
        messages.success(request, message, extra_tags='alert-success')
    except:
        scrape_lacrosse()

    next = request.POST.get('next', reverse('temperature_monitor:query_list'))
    return HttpResponseRedirect(next)


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
        context['latest_query'] = latest_query()
        context['update_delay'] = 60 * getattr(
            settings, 'LA_CROSSE_ALERTS_UPDATE_DELAY', 5)
        return context


class GatewayList(PermissionRequiredMixin, ListView):
    context_object_name = 'gateway_list'
    model = Gateway
    permission_denied_message = ('You do not have permission to view gateway '
        'lists.')
    permission_required = 'temperature_monitor.view_gateway'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['latest_query'] = latest_query()
        context['update_delay'] = 60 * getattr(
            settings, 'LA_CROSSE_ALERTS_UPDATE_DELAY', 5)
        return context


class QueryList(PermissionRequiredMixin, ListView):
    context_object_name = 'query_list'
    model = Query
    permission_denied_message = ('You do not have permission to view query '
        'lists.')
    permission_required = 'temperature_monitor.view_query'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['latest_query'] = latest_query()
        context['update_delay'] = 60 * getattr(
            settings, 'LA_CROSSE_ALERTS_UPDATE_DELAY', 5)
        return context


class SensorDetail(PermissionRequiredMixin, DetailView):
    context_object_name = 'sensor'
    model = Sensor
    permission_denied_message = ('You do not have permission to view sensor '
        'details.')
    permission_required = 'temperature_monitor.view_sensor'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['latest_query'] = latest_query()
        context['update_delay'] = 60 * getattr(
            settings, 'LA_CROSSE_ALERTS_UPDATE_DELAY', 5)
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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['latest_query'] = latest_query()
        context['update_delay'] = 60 * getattr(
            settings, 'LA_CROSSE_ALERTS_UPDATE_DELAY', 5)
        return context
