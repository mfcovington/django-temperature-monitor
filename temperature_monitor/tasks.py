from django.core import management

from celery import shared_task

from .management.commands import scrape_lacrosse


@shared_task
def update(force=False):
    """
    Query La Crosse Alerts site.
    """
    return management.call_command(scrape_lacrosse.Command(), force=force)
