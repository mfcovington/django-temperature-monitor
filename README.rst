**************************
django-temperature-monitor
**************************

``django-temperature-monitor`` is a Django app to simultaneously monitor multiple La Crosse Alerts sensors and keep an extended history of data points.

Source code is available on GitHub at `mfcovington/django-temperature-monitor <https://github.com/mfcovington/django-temperature-monitor>`_.

.. contents:: :local:


Installation
============

.. **PyPI**

.. .. code-block:: sh

..     pip install django-temperature-monitor


**GitHub (development branch)**

.. code-block:: sh

    pip install git+http://github.com/mfcovington/django-temperature-monitor.git@develop


Configuration
=============

Add ``temperature_monitor`` to ``INSTALLED_APPS``in ``settings.py``:

.. code-block:: python

    INSTALLED_APPS = (
        ...
        'project_home_tags',
        'temperature_monitor',
    )


If using ``project_home_tags`` in your project, specify the ``PROJECT_HOME_NAMESPACE`` and, optionally, ``PROJECT_HOME_LABEL`` in ``settings.py`` (see `PyPI <https://pypi.org/project/django-project-home-templatetags/>`_ for more information):

.. code-block:: python

    PROJECT_HOME_NAMESPACE = 'project_name:index_view'
    PROJECT_HOME_LABEL = 'Homepage'    # Optional; Default is 'Home'


Specify the La Crosse Alerts login credentials in ``settings.py``:

.. code-block:: python

    LA_CROSSE_ALERTS_USERNAME = ''
    LA_CROSSE_ALERTS_PASSWORD = ''


Specify the preferred unit of temperature (``C`` or ``F``) in ``settings.py``:

.. code-block:: python

    TEMPERATURE_MONITOR_UNIT = 'C'


Set the (headless) browser to use for accessing the La Crosse Alerts site ``settings.py`` to ``chrome`` or ``firefox`` (default):

.. code-block:: python

    SELENIUM_BROWSER = 'chrome'


Add the ``temperature_monitor`` URL to the site's ``urls.py``:

.. code-block:: python

    from django.urls import include, path

    urlpatterns = [
        ...
        path('temperatures/', include('temperature_monitor.urls', namespace='temperature-monitor')),
    ]


Migrations
==========

Create migrations for ``temperature_monitor``, if necessary:

.. code-block:: sh

    python manage.py makemigrations temperature_monitor


Perform migrations for ``temperature_monitor`` and dependencies:

.. code-block:: sh

    python manage.py migrate


Usage
=====

- Start the development server:

.. code-block:: sh

    python manage.py runserver


- Visit: ``http://127.0.0.1:8000/temperatures/``


*Version 0.1.0*
