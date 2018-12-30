import datetime
import pytz
import re
import time

from django.conf import settings
from django.core.management.base import BaseCommand

import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver

from ...models import Sensor, TimePoint

SELENIUM_BROWSER = getattr(settings, 'SELENIUM_BROWSER', 'firefox')
if SELENIUM_BROWSER == 'chrome':
    from selenium.webdriver.chrome.options import Options
if SELENIUM_BROWSER == 'firefox':
    from selenium.webdriver.firefox.options import Options


def convert_f_to_c(temperature):
    return 5 * temperature / 9 - 32


def get_alert_settings(soup, device_id, device_type, input_type):
    INPUT_TYPES = {
        'sensor': 1,
        'probe': 2,
        'humidity': 3,
    }
    alert_settings = soup.find('li', {'id': 'device_input_{}_{}_{}'.format(
        INPUT_TYPES[input_type], device_type, device_id)})
    alert_max = alert_settings.attrs['data-alertmax']
    alert_min = alert_settings.attrs['data-alertmin']
    alert_units = alert_settings.attrs['data-units']
    alert_units = alert_settings.attrs['data-units']

    if alert_min == 'null':
        alert_min = None
    elif alert_units == '°F':
        alert_min = convert_f_to_c(alert_min)

    if alert_max == 'null':
        alert_max = None
    elif alert_units == '°F':
        alert_max = convert_f_to_c(alert_max)

    return (alert_min, alert_max)


class Command(BaseCommand):
    def handle(self, **options):
        username = settings.LA_CROSSE_ALERTS_USERNAME
        password = settings.LA_CROSSE_ALERTS_PASSWORD

        url = 'http://www.lacrossealertsmobile.com/v1.2/'
        datetime_format = '%m/%d/%Y %I:%M %p'
        page_load_delay = 15
        tz = pytz.timezone(settings.TIME_ZONE)

        print('Connecting to La Crosse Alerts site.')
        options = Options()
        options.set_headless(True)
        if SELENIUM_BROWSER == 'chrome':
            driver = webdriver.Chrome(options=options)
        if SELENIUM_BROWSER == 'firefox':
            driver = webdriver.Firefox(options=options)
        driver.get(url)
        driver.find_element_by_id('iLogEmail').send_keys(username)
        driver.find_element_by_id('iLogPass').send_keys(password)
        driver.find_element_by_css_selector(
            '#userLogin form button[type="submit"]').click()

        # Need to wait for data tables to populate
        print('Waiting for page to load.')
        time.sleep(page_load_delay)

        # This can also be used to refresh the page and get the times again
        print('Collecting data.')
        soup = BeautifulSoup(driver.page_source, 'lxml')

        device_list = soup.find_all('li', {'class': 'device_list'})

        print('Updating database.')
        for device in device_list:
            device_id = device.attrs['data-id']
            device_name = device.get_text(strip=True)
            device_type = device.attrs['data-device-type']

            sensor, created = Sensor.objects.get_or_create(
                serial_number=device_id)
            if created or sensor.location is not device_name:
                sensor.device_type = device_type
                sensor.location = device_name

            sensor.link = soup.select_one(
                'tr.HiddenForPWS-{} td.notiLink'.format(device_id)).text
            sensor.battery = soup.select_one(
                'tr.HiddenForPWS-{} td.notiBattery'.format(device_id)).text

            (probe_min, probe_max) = get_alert_settings(
                soup, device_id, device_type, 'probe')
            sensor.probe_alert_min_celsius_unitless = probe_min
            sensor.probe_alert_max_celsius_unitless = probe_max

            (sensor_min, sensor_max) = get_alert_settings(
                soup, device_id, device_type, 'sensor')
            sensor.sensor_alert_min_celsius_unitless = sensor_min
            sensor.sensor_alert_max_celsius_unitless = sensor_max

            (humidity_min, humidity_max) = get_alert_settings(
                soup, device_id, device_type, 'humidity')
            sensor.humidity_alert_min_unitless = humidity_min
            sensor.humidity_alert_max_unitless = humidity_max

            sensor.save()

            device_table = soup.find(
                'tbody', {'id': 'dTable_{}'.format(device_id)}).parent
            df = pd.read_html(str(device_table))[0]

            for index, row in df.iterrows():
                timestamp = datetime.datetime.strptime(
                    row['Time Seen'], datetime_format)
                timepoint, created = TimePoint.objects.get_or_create(
                    sensor=sensor, time=tz.localize(timestamp))
                if created:
                    humid_re = re.compile('(-?\d+\.\d)%')
                    temp_re = re.compile('(-?\d+\.\d)°(C|F)')

                    m_humidity = humid_re.match(row['Humidity'])
                    if m_humidity is None:
                        timepoint.humidity_unitless = None
                    else:
                        timepoint.humidity_unitless = m_humidity[1]

                    m_probe_temp = temp_re.match(row['Probe'])
                    if m_probe_temp is None:
                        timepoint.probe_celsius_unitless = None
                    elif m_probe_temp[2] == 'C':
                        timepoint.probe_celsius_unitless = m_probe_temp[1]
                    elif m_probe_temp[2] == 'F':
                        timepoint.probe_celsius_unitless = convert_f_to_c(
                            m_probe_temp[1])

                    m_sensor_temp = temp_re.match(row['Sensor'])
                    if m_sensor_temp is None:
                        timepoint.sensor_celsius_unitless = None
                    elif m_sensor_temp[2] == 'C':
                        timepoint.sensor_celsius_unitless = m_sensor_temp[1]
                    elif m_sensor_temp[2] == 'F':
                        timepoint.sensor_celsius_unitless = convert_f_to_c(
                            m_sensor_temp[1])

                    timepoint.save()
                else:
                    break

        driver.quit()

