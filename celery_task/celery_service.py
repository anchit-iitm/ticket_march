from celery import Celery
# from flask import current_app as app
from mailer import mail, Message

celery = Celery('tasks', broker='redis://localhost:6379/0')  # Replace 'redis://localhost:6379/0' with your Redis URL if needed

@celery.task
def add_numbers(x, y):
    result = x + y
    print(f"Result of addition: {result}")
    return result

@celery.task
def send_test_email():
    # with app.app_context():  # Create Flask app context for mail sending
    # Replace 'recipient@example.com' with the actual recipient address
    recipient = 'recipient@example.com'
    subject = 'Test Email from Flask Server (Celery Task)'
    body = 'This is a test email sent from your Flask server using a Celery task.'

    message = Message(subject, recipients=[recipient], body=body)
    # mail = Mail(app)  # Create a Mail instance within the context
    mail.send(message)

    return f"Test email sent successfully to {recipient}!"