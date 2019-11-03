from django.conf import settings
from django.core import management
from django.core.mail import EmailMessage

from celery import shared_task

from .management.commands import scrape_lacrosse
from .models import Gateway, Query, Sensor, TimePoint


@shared_task
def email_alerts(
        battery=True, email=True, gateway=True, humidity=True, link=True,
        probe=True, query=True, sensor=True, sms=True, subject_prefix='',
        time_since=True):
    """
    Email current alerts.
    """
    alerts = get_alerts(
        battery=battery, gateway=gateway, humidity=humidity, link=link,
        probe=probe, query=query, sensor=sensor, time_since=time_since)

    body = ''

    if alerts['gateways']:
        body += '\nGateway Alerts\n\n'

        for g_id, g_alerts in alerts['gateways'].items():
            g = Gateway.objects.get(id=g_id)
            body += '\t- {}\n'.format(g.serial_number)
            for alert_type, alert_status in g_alerts.items():
                body += '\t\t- {}: {}\n'.format(alert_type, alert_status)

    if alerts['queries']:
        body += '\nQuery Alerts\n\n'

        for q_id, q_alerts in alerts['queries'].items():
            q = Query.objects.get(id=q_id)
            body += '\t- {} ({})\n'.format(q.time, q.time_since)
            for alert_type, alert_status in q_alerts.items():
                body += '\t\t- {} ({})\n'.format(alert_type, alert_status)

    if alerts['sensors']:
        body += '\nSensor Alerts\n\n'

        for s_id, s_alerts in alerts['sensors'].items():
            s = Sensor.objects.get(id=s_id)
            body += '\t- {}\n'.format(s.location)
            for alert_type, alert_status in s_alerts.items():
                body += '\t\t- {}: {}\n'.format(alert_type, alert_status)

    if body:
        EMAIL_HOST_USER = getattr(settings, 'EMAIL_HOST_USER', None)
        address_list = []
        if email:
            address_list.extend(settings.ALERT_EMAIL_LIST)
        if sms:
            address_list.extend(settings.ALERT_SMS_LIST)
        email = EmailMessage(
            '{}Refrigeration Alerts Summary'.format(subject_prefix), body,
            from_email=EMAIL_HOST_USER, to=address_list)
        email.send()


@shared_task
def email_alerts_maintenance():
    """
    Email current maintenance alerts.
    """
    email_alerts(probe=False, sensor=False, sms=False)


@shared_task
def email_alerts_urgent():
    """
    Email current urgent alerts.
    """
    email_alerts(
        battery=False, gateway=False, humidity=False, link=False, query=False,
        subject_prefix='[URGENT] ', time_since=False)


@shared_task
def get_alerts(
    battery=True, gateway=True, humidity=True, link=True, probe=True,
    query=True, sensor=True, time_since=True):
    """
    Get current alerts.
    """
    alerts = {'gateways': {}, 'queries': {}, 'sensors': {}}

    if gateway:
        for g in Gateway.objects.all():
            if g.alert:
                alerts['gateways'][g.id] = {'Last Seen': g.time_since_last_seen}

    for s in Sensor.objects.all():
        s_alerts = {}
        if battery:
            if s.battery != 'Good':
                s_alerts['Battery Status'] = s.battery
        if humidity and s.humidity_alert:
            s_alerts['Humidity'] = s.humidity
        if link:
            pass
        if probe and s.probe_alert:
            s_alerts['Probe'] = s.probe_temp
        if sensor and s.sensor_alert:
            s_alerts['Sensor'] = s.sensor_temp
        if time_since and s.alert_time:
            s_alerts['Last Seen'] = s.time_since_last_seen
        if s_alerts:
            alerts['sensors'][s.id] = s_alerts

    if query:
        q = Query.objects.latest()
        q_alerts = {}
        if q.gateway_alert:
            q_alerts['Gateway Count'] = q.gateway_count
        if q.query_alert:
            q_alerts['Query Duration'] = 'NA'
        if q.sensor_alert:
            q_alerts['Sensor Count'] = q.sensor_count
        if q.timepoint_alert:
            q_alerts['Timepoint Count'] = q.timepoint_count
        if q_alerts:
            alerts['queries'][q.id] = q_alerts

    return alerts


@shared_task
def update(force=False):
    """
    Query La Crosse Alerts site.
    """
    return management.call_command(scrape_lacrosse.Command(), force=force)
