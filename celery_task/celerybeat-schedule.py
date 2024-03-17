from celery.schedules import crontab
from celery_service import celery

celery.conf.beat_schedule = {
    'add_numbers_daily_at_7pm': {
        'task': 'celery_service.send_test_email',  # Name of the Celery task
        'schedule': crontab(hour=13, minute=17),  # Run at 7 PM daily
        # 'args': (4, 5),  # Arguments to pass to the task
    }
}
