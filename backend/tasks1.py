from celery import Celery
from flask import current_app as app
from celery.schedules import crontab
from datetime import datetime

celery = Celery("Application Jobs")
celery.conf.broker_url = 'redis://localhost:6379/1'
celery.conf.backend = 'redis://localhost:6379/2'

celery.conf.beat_schedule = {
    'add': {
        'task': 'tasks.add',
        'schedule': crontab(hour='13', minute='49'),
    },
}

class ContextTask(celery.Task):
    def __call__(self, *args, **kwargs):
        with app.app_context():
            return self.run(*args, **kwargs)

@celery.task
def add():
    a=1
    b=2
    return (a+b)