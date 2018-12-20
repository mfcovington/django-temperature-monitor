import datetime
import pytz
import re
import time

from django.conf import settings
from django.core.management.base import BaseCommand

import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.firefox.options import Options

from ...models import Sensor, TimePoint


def convert_f_to_c(temperature):
    return 5 * temperature / 9 - 32


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

            sensor, created = Sensor.objects.get_or_create(
                serial_number=device_id)
            if created or sensor.location is not device_name:
                sensor.device_type = device.attrs['data-device-type']
                sensor.location = device_name
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

                    m_humidity = humid_re.match('42.3%')
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

