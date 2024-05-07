from __future__ import absolute_import, unicode_literals

import os
from celery import Celery
from celery.schedules import crontab
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'SentixSagePro.settings')

app = Celery('SentixSagePro')
CELERY_BEAT_SCHEDULER = 'django_celery_beat.schedulers.DatabaseScheduler'
app.conf.enable_utc = False
app.conf.update(timezone='Asia/Kolkata')

app.config_from_object(settings, namespace='CELERY')

app.conf.beat_schedule = {
    'collect-daily-data': {
        'task': 'Task.tasks.collect_daily_data',
        'schedule': crontab(hour=17, minute=3),
    },
    'feature-engineering-and-model-training': {
        'task': 'Task.tasks.feature_engineering_and_model_training',
        'schedule': crontab(hour=17, minute=10),  # Schedule to run at midnight
    },
}

app.autodiscover_tasks()


# Task setting
@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
