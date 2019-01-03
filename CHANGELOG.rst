Revision History
================

0.2.0 2019-01-02

- Access records from front end, not just admin
- Track gateways and query stats
- Allow the 15 second page load delay to be overridden with ``settings.LA_CROSSE_ALERTS_PAGE_LOAD_DELAY``
- Prevent queries within 5 minutes of previous update
    - Override delay with ``settings.LA_CROSSE_ALERTS_UPDATE_DELAY``
    - Force early query via CLI with ``python manage.py scrape_lacrosse --force``
- Set the (headless) browser to use for accessing the La Crosse Alerts site to 'chrome' or 'firefox' (default)
- Fix bug where humidity was always 42.3%
- Fix loss of time zone correction


0.1.0 2018-12-20

- A Django app to simultaneously monitor multiple La Crosse Alerts sensors and keep an extended history of data points
