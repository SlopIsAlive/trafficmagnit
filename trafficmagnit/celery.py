from datetime import timedelta
import os

from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "trafficmagnit.settings")

app = Celery("trafficmagnit")
app.config_from_object("django.conf:settings", namespace="CELERY")

app.autodiscover_tasks()

app.conf.beat_schedule = {
    "refresh-exchange-rates": {
        "task": "currency.fetch_rates",
        "schedule": timedelta(hours=1),
    },
}
