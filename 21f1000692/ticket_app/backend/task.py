from celery import Celery

from flask import current_app as app

celery = Celery("Application Jobs")
celery.conf.update(
    broker_url='redis://localhost:6379/1',
    result_backend ='redis://localhost:6379/2'
)
 
class ContextTask(celery.Task):
    def __call__(self, *args, **kwargs):
        with app.app_context():
            return self.run(*args, **kwargs)

from celery.schedules import crontab

celery.conf.beat_schedule = {
    'test_task': {
        'task': 'task.add',
        'schedule': crontab(hour=15, minute=57),  # its using utc time
    },
    'my_task': {
        'task': 'task.simple_py_fn',
        'schedule': crontab(hour=14, minute=8),  # its using utc time
    },
    'mail_test_with_some_data': {
        'task': 'mad1_ver.send_test_email',
        'schedule': crontab(hour=13, minute=18),  # its using utc time
    },
}

@celery.task
def add():
    a=1
    b=2
    return (a+b)

@celery.task
def simple_py_fn():
    var1 = "test"
    var2 = "test2"
    print(var1+var2)


'''from mail_support import  Message, mail
# @celery.task
# def mail_test():
#     with app.app_context():
#         send_test_email()
#         return "Mail sent successfully"

@celery.task
def mail_test_with_some_data():
    # with app.app_context():
        # var1 = Venue.query.first()
    recipient_email = 'user1@gmail.com'
    subject = "var1.name"

    msg = Message(subject,recipients=[recipient_email])
    mail.send(msg)
    return "the mail was sent successfully"'''

