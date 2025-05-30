import os
from celery import Celery
from celery.schedules import crontab


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

app = Celery('core')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

# Celery Beat Schedule (in code)
app.conf.beat_schedule = {
    'refresh-top-districts-every-hour': {
        'task': 'core.tasks.refresh_top_districts',
        'schedule': crontab(minute=0),  # every hour, at minute 0
    },
}