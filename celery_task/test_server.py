from flask import Flask
from mailer import mail, Message

app = Flask(__name__)

# Flask-Mail configuration
app.config['MAIL_SERVER'] = 'localhost'
app.config['MAIL_PORT'] = 1025
app.config['MAIL_USE_TLS'] = False  # Adjust if your local SMTP server requires TLS
app.config['MAIL_USE_SSL'] = False   # Adjust if your local SMTP server requires SSL
app.config['MAIL_USERNAME'] = 'your_email@example.com'  # Replace with your email address
app.config['MAIL_PASSWORD'] = 'your_password'        # Replace with your email password
app.config['MAIL_DEFAULT_SENDER'] = 'no-reply@example.com'

# Optional: Create a Mail instance for better organization
mail.init_app(app)

@app.route('/test')
def test_endpoint():
    return "Hello from the test server!"

@app.route('/send-mail')
def send_mail():
    # Replace 'recipient@example.com' with the actual recipient address
    recipient = 'recipient@example.com'
    subject = 'Test Email from Flask Server'
    body = 'This is a test email sent from your Flask server.'

    message = Message(subject, sender=app.config['MAIL_USERNAME'], recipients=[recipient], body=body)
    mail.send(message)

    return 'Email sent successfully!'

from celery_service import add_numbers, send_test_email # Import the Celery tasks

@app.route('/trigger-task')
def trigger_task():
    result = add_numbers.delay(4, 5)  # Call the task asynchronously
    return f"Task triggered successfully! Result: {result.id}"

@app.route('/send-test-email-celery')
def send_test_email_celery():
    send_test_email.delay()  # Call the Celery task asynchronously
    return 'Test email sent using Celery task (background process).'


if __name__ == '__main__':
    app.run(debug=True)
