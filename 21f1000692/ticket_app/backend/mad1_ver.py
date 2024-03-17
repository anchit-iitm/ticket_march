import os, bcrypt, secrets, json
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session, render_template_string, send_from_directory, send_file
from mad1_ver_models import *
from flask_security import Security, SQLAlchemyUserDatastore, login_required, roles_required, UserMixin, current_user, login_user, logout_user, auth_token_required
from flask_cors import CORS
from datetime import datetime, timedelta
from sqlalchemy import or_

from flask_caching import Cache

from flask_mail import Mail, Message


# from task import celery, ContextTask
from celery import Celery
from celery.schedules import crontab


app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///./db1.sqlite3"

app.config['SECRET_KEY'] = 'super-secret'
app.config['SECURITY_PASSWORD_HASH'] = 'bcrypt'
app.config['SECURITY_PASSWORD_SALT'] = 'secrets.SystemRandom().getrandbits(128)'
app.config['SECURITY_TOKEN_AUTHENTICATION_HEADER'] = 'Authorization'

app.config['MAIL_SERVER'] = 'localhost'
app.config['MAIL_PORT'] = 1025  # MailHog SMTP port
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = False
app.config['MAIL_USERNAME'] = None
app.config['MAIL_PASSWORD'] = None
app.config['MAIL_DEFAULT_SENDER'] = 'no-reply@example.com'


db.init_app(app)
CORS(app)


celery = Celery(app.name, broker='redis://localhost:6379/1', backend='redis://localhost:6379/2')

 # Configure Celery Beat
celery.conf.beat_schedule = {
    'automate_monthly_email_everyday':{
        'task': 'mad1_ver.send_monthly_report',
        'schedule': crontab(hour=14, minute=40)
    },
    'automate_monthly_email':{
        'task': 'mad1_ver.send_monthly_report',
        'schedule': crontab(hour=14, minute=41, day_of_month=16)
    },
}


mail=Mail()
mail.init_app(app)

cache = Cache(app, 
              config={
                  'CACHE_TYPE': 'redis',
    'CACHE_REDIS_URL': 'redis://localhost:6379/0',  # Update with your Redis server URL
    'CACHE_DEFAULT_TIMEOUT': 600,  # Default cache timeout in seconds (10 mins)})
              })
#_______________________________________________________________________________________________________#


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

@app.route('/test_mail')
def send_test_email():
    var1 = Venue.query.first()
    print(var1.name)
    
    recipient_email = 'user1@gmail.com'
    subject = "Reminder: Visit our website for new shows!"
    email_body = "Hello,\n\nThis is a reminder to visit our website for new shows!\n\nBest regards,\nT"

    msg = Message(subject=subject, recipients=[recipient_email])
    msg.body = email_body
    mail.send(msg)
    return "Email sent successfully!"

# from task import add, simple_py_fn, mail_test_with_some_data

@celery.task
def mail_test_with_some_data():
    with app.app_context():
        var1 = Venue.query.first()
        recipient_email = 'user1@gmail.com'
        email_body = "Hello,\n\nThis is a reminder to visit our website for new shows!\n\nBest regards,\nT"
        subject = var1.name

        msg = Message(subject=subject,recipients=[recipient_email])
        msg.body = email_body
        mail.send(msg)
        return "the mail was sent successfully"
    

@celery.task
def send_monthly_report():
    with app.app_context():
        def monthly_report(user, bookings):
            # Create the HTML structure for the report
            report = "<html><body>"
            report += f"<h2>Monthly Entertainment Report for {user.email}</h2>"
            report += "<ul>"
            print(report)

            for booking in venues:
                # show = Show.query.first()
                report += f"<li>Booking ID: {booking.id}</li>"
                report += f"<li>Booking ID: {booking.name}</li>"
                report += f"<li>Booking ID: {booking.description}</li>"
                report += f"<li>Booking ID: {booking.address}</li>"
                report += f"<li>Booking ID: {booking.capacity}</li>"
                
                # report += f"<li>Show Name: {show.name}</li>"
                # report += f"<li>Booking Date: {booking.booking_date.strftime('%Y-%m-%d')}</li>"
                # report += f"<li>Number of Tickets: {booking.number_of_tickets}</li>"
                # report += f"<li>Ticket Price: {show.ticket_price}</li>"
                # report += f"<li>Total Amount: {booking.total_amount}</li>"
                report += "</ul>"
                report += "<hr>"

            report += "</ul>"
            report += "</body></html>"

            return report
        # # Get the current date and the start date of the previous month
        # current_date = datetime.utcnow()
        # start_of_previous_month = (current_date - timedelta(days=current_date.day)).replace(day=1)

        # Get all users
        users = User.query.all()

        for user in users:
            # Query bookings made by the user in the previous month
            venues = Venue.query.filter().all()

            if venues:
                # Generate the HTML report
                html_report = monthly_report(user, venues)
                # report = "ok"

                # Send the report as an email
                subject = "Your Monthly Entertainment Report for the previous month"
                recipients = [user.email]
                msg = Message(subject=subject, recipients=recipients)
                msg.body = "check the html part of the email"
                msg.html = html_report
                mail.send(msg)

                print(f"Monthly report sent to User ID: {user.id}")


# from task import add

@app.route('/test_celery')
def test_celery_task():
    # mail_test_with_some_data.delay()
    # add.delay()
    # simple_py_fn.delay()
    send_monthly_report.delay()

    return "the test task queued!"



# Associate the roles with permissions
def create_roles():
    roles_permissions = {
        'admin': ['admin-access'],
        'user': ['user-access']
    }
    for role_name, permissions in roles_permissions.items():
        role = Role.query.filter_by(name=role_name).first()
        if not role:
            role = Role(name=role_name, permissions=','.join(permissions))
            db.session.add(role)
    db.session.commit()

'''def create_role_v2():
    admin_role = user_datastore.find_or_create_role(name='admin', permissions=['admin-access']) 
    user_role = user_datastore.find_or_create_role(name='user', permissions=['user-access'])
    db.session.commit()
    ''' 

# Create the User and Role models
user_datastore = SQLAlchemyUserDatastore(db, User, Role)
security = Security(app, user_datastore)

# Create the roles and assign them to the user
with app.app_context():
        db.create_all()
        create_roles()

        # Check if any user with the role 'admin' exists
        admin_role = Role.query.filter_by(name='admin').first()
        admin_user = User.query.filter(User.roles.any(id=admin_role.id)).first()

        # If there is no admin user, create one
        if not admin_user:
            admin_email = 'abc@abc.com'  # Change this email as needed
            admin_password = 'abc'
            hashed_password = bcrypt.hashpw(admin_password.encode('utf-8'), bcrypt.gensalt())

            user_user = user_datastore.create_user(email=admin_email, password=hashed_password)
            user_datastore.add_role_to_user(user_user, 'admin')
            db.session.commit()

#___________________________________________________________________________________________________________#

@app.route('/api/register', methods=['POST'])
def user_register():
    data = request.get_json()
    email = data['email']
    password = data['password']
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    try:
        user_user = user_datastore.create_user(email=email, password=hashed_password)
        user_datastore.add_role_to_user(user_user, 'user')
        db.session.commit()
        user_id = User.query.filter_by(email=email).first().id
        activity = UserActivity(user_id=user_id, activity_type='registered')
        db.session.add(activity)
        db.session.commit()
        return jsonify({'message': 'User has been registered successfully'}), 200
    except:
        # Handle the case when the email already exists
        return jsonify({'message': 'This email is already registered. Please use a different email.'}), 400

@app.route('/api/login', methods=['POST'])
def user_login():
    data = request.get_json()
    email = data['email']
    password = data['password']
    user = user_datastore.find_user(email=email)

    if user :
        if bcrypt.checkpw(password.encode('utf-8'), user.password):
            auth_token = user.get_auth_token()
            login_user(user)
            activity = UserActivity(user_id=user.id, activity_type='login')
            db.session.add(activity)
            db.session.commit()
            return jsonify({'message': 'User logged in successfully', 'auth_token': auth_token, 'id': current_user.id,
            'email': current_user.email,
            'roles': [role.name for role in current_user.roles]}), 200
        else:
            return jsonify({'message': 'Invalid email or password.'}), 400
    else:
        return jsonify({'message': 'User not registered please register!'}), 400
 
@app.route('/api/logout', methods=['POST'])
def user_logout():
    logout_user()
    data = request.get_json()
    userid = data.get('uid')
    activity = UserActivity(user_id=userid, activity_type='logout')
    db.session.add(activity)
    db.session.commit()
    return jsonify({'message': 'User logged out successfully'}), 200


@app.route('/api/venues-and-shows', methods=['GET'])
# @roles_accepted('admin')  # Only users with 'admin' role can access this endpoint
# @auth_token_required
@cache.cached(timeout=60)  # Cache for 10 seconds
def get_venues_and_shows():
    venues = Venue.query.all()
    shows = Show.query.all()

    venues_data = []
    for venue in venues:
        venue_info = {
            'id': venue.id,
            'name': venue.name,
            'address': venue.address,
            'capacity': venue.capacity,
            'description': venue.description,
            'shows': []
        }
        for show in shows:
            if show.venue_id == venue.id:
                show_info = {
                    'id': show.id,
                    'name': show.name,
                    'description': show.description,
                    'rating': show.rating,
                    'tags': show.tags,
                    'ticket_price': show.ticket_price,
                    'total_tickets': show.total_tickets,
                    'avialable_tickets': show.avail_ticket,
                }
                venue_info['shows'].append(show_info)
        venues_data.append(venue_info)

    return jsonify(venues_data), 200

@app.route('/api/create-venue', methods=['POST'])
# @roles_required('admin')  # Only users with 'admin' role can access this endpoint
# @auth_token_required
def create_venue():
    data = request.get_json()
    name = data['name']
    address = data['address']
    capacity = data['capacity']
    description = data['description']

    try:
        # Create a new venue record in the database
        venue = Venue(name=name, address=address, capacity=capacity, description=description)
        db.session.add(venue)
        db.session.commit()

        return jsonify({'message': 'Venue created successfully'}), 200
    except:
        # Handle the case when error
        return jsonify({'message': 'some error occured.'}), 400

@app.route('/api/venue/<int:venue_id>', methods=['GET', 'PUT'])
# @roles_required('admin')  # Only users with 'admin' role can access this endpoint
# @auth_token_required
def venue_details(venue_id):
    venue = Venue.query.get(venue_id) # Venue.query.filter_by(id=venue_id).first()
    if not venue:
        return jsonify({'message': 'Venue not found'}), 404

    if request.method == 'GET':
        venue_info = {
            'id': venue.id,
            'name': venue.name,
            'address': venue.address,
            'capacity': venue.capacity,
            'description': venue.description,
        }
        return jsonify(venue_info), 200

    if request.method == 'PUT':
        data = request.get_json()
        capacity = data.get('capacity')
        description = data.get('description')

        if capacity is not None:
            venue.capacity = capacity
        if description is not None:
            venue.description = description

        db.session.commit()
        return jsonify({'message': 'Venue updated successfully'}), 200


@app.route('/api/venue/<int:venue_id>/show/<int:show_id>', methods=['GET','PUT'])
@roles_required('admin')  # Only users with 'admin' role can access this endpoint
# @auth_token_required
def modify_show(show_id, venue_id):
    # data = request.get_json()
    show = Show.query.filter_by(id=show_id, venue_id=venue_id).first()

    if not show:
        return jsonify({'message': 'Show not found'}), 404
    
    if request.method == 'GET':
        show_info = {
            'id': show.id,
            'name': show.name,
            'description': show.description,
            'rating': show.rating,
            'tags': show.tags,
            'ticket_price': show.ticket_price,
            'venue_id': show.venue_id,
            'total_tickets': show.total_tickets
        }
        return jsonify(show_info), 200
    
    if request.method == 'PUT':
        data = request.get_json()
        description = data.get('description')
        rating = data.get('rating')
        tags = data.get('tags')
        ticket_price = data.get('ticket_price')
        total_tickets = data.get('total_tickets')

        if rating is not None:
            show.rating = rating
        if tags is not None:
            show.tags = tags
        if ticket_price is not None:
            show.ticket_price = ticket_price
        if total_tickets is not None:
            show.total_tickets = total_tickets
            show.avail_ticket = total_tickets
        if description is not None:
            show.description = description
      
        try:
            db.session.commit()
            return jsonify({'message': 'Show modified successfully'}), 200
        except:
            db.session.rollback()
            return jsonify({'message': 'Error modifying show'}), 500



@app.route('/api/shows', methods=['POST'])
@roles_required('admin')  # This ensures only users with the 'admin' role can access this endpoint
# @auth_token_required
def createshow():
    data = request.get_json()
    name = data['name']
    description = data['description']
    rating = data['rating']
    tags = data['tags']
    ticket_price = data['ticket_price']
    total_tickets = data['total_tickets']
    venue_id = data['venue_id']
    try:
        new_show = Show(name=name, rating=rating, tags=tags, ticket_price=ticket_price, venue_id=venue_id, total_tickets=total_tickets, avail_ticket=total_tickets, description=description)
        db.session.add(new_show)
        db.session.commit()
        return jsonify({'message': 'Show has been created successfully'}), 200
    except Exception as e:
        print(e)
        db.session.rollback()
        # Handle any error that may occur during show creation
        return jsonify({'message' : 'Error creating show'}), 500


@app.route('/api/venue/<int:venue_id>/show/<int:show_id>', methods=['DELETE'])
@roles_required('admin')  # Only users with 'admin' role can delete a show
# @auth_token_required
def delete_show(venue_id, show_id):
    show = Show.query.filter_by(id=show_id, venue_id=venue_id).first()

    if not show:
        return jsonify({'message': 'Show not found'}), 404

    try:
        db.session.delete(show)
        db.session.commit()
        return jsonify({'message': 'Show deleted successfully'}), 200
    except:
        db.session.rollback()
        return jsonify({'message': 'Error deleting show'}), 500

@app.route('/api/venue/<int:venue_id>', methods=['DELETE'])
@roles_required('admin')  # Only users with 'admin' role can delete a venue
# @auth_token_required
def delete_venue(venue_id):
    venue = Venue.query.get(venue_id)

    if not venue:
        return jsonify({'message': 'Venue not found'}), 404

    try:
        # Delete all shows associated with the venue
        Show.query.filter_by(venue_id=venue_id).delete()

        # Delete the venue itself
        db.session.delete(venue)
        db.session.commit()

        return jsonify({'message': 'Venue and associated shows deleted successfully'}), 200
    except:
        db.session.rollback()
        return jsonify({'message': 'Error deleting venue'}), 500


@app.route('/api/search/theatres', methods=['GET'])
# # @auth_token_required
def search_theatres():
    location = request.args.get('location', '').strip()

    if location:
        theatres = Venue.query.filter(or_(
            Venue.name.ilike(f'%{location}%'),
            Venue.address.ilike(f'%{location}%')
        )).all()
    else:
        theatres = []

    return jsonify([theatre.serialize() for theatre in theatres])

@app.route('/api/search/shows', methods=['GET'])
# # @auth_token_required
def search_shows():
    tags = request.args.get('tags', '').strip()
    rating = request.args.get('rating', 0.0)

    if tags:
        shows = Show.query.filter(Show.tags.ilike(f'%{tags}%')).all()
    else:
        shows = []

    # Filter shows by rating
    filtered_shows = [show for show in shows if show.rating >= float(rating)]

    return jsonify([show.serialize() for show in filtered_shows])

#___________________________________________________________________________________________________________________________________________________________________________________user#

@app.route('/api/venues', methods=['GET'])
# @auth_token_required
# @cache.cached(timeout=10)  # Cache for 10 minutes
def list_venues():
    def extract_venue_data(venue):
        return {
            'id': venue.id,
            'name': venue.name,
            'address': venue.address,
            'description': venue.description,
        }

    def extract_shows_for_venue(venue):
        shows = Show.query.filter_by(venue_id=venue.id).all()
        return [
            {
                'id': show.id,
                'name': show.name,
                'description': show.description,
                'rating': show.rating,
                'tags': show.tags,
                'ticket_price': show.ticket_price,
                'total_tickets': show.avail_ticket,
            }
            for show in shows
        ]
    try:
        venues = Venue.query.all()
        venues_data = []

        for venue in venues:
            venue_data = extract_venue_data(venue)
            venue_data['shows'] = extract_shows_for_venue(venue)
            venues_data.append(venue_data)

        return jsonify(venues_data), 200

    except Exception as e:
        return jsonify({'message': 'An error occurred while fetching venues'}), 500

@app.route('/api/show/<show_id>', methods=['GET'])
# @auth_token_required
def list_show(show_id):
    # data = request.get_json()
    # show_id = data.get('show_id')
    show = db.session.get(Show, show_id)
    if not show:
        return jsonify({'message': 'Show not found'}), 404
    try:
        show_data = {
            'id': show.id,
            'name': show.name,
            'description': show.description,
            'rating': show.rating,
            'tags': show.tags,
            'ticket_price': show.ticket_price,
            'total_tickets': show.avail_ticket,
        }
        return jsonify(show_data), 200
    except Exception as e:
        return jsonify({'message': 'An error occurred while fetching show'}), 500

@app.route('/api/bookings', methods=['POST'])
# @auth_token_required
def create_booking():
    data = request.get_json()
    show_id = data.get('show_id')
    num_tickets = int(data['number_of_tickets'])
    userid = data.get('uid')
    # print(current_user.id)
    # show = Show.query.get(show_id)
    show = db.session.get(Show, show_id)

    if not show:
        return jsonify({'message': 'Show not found'}), 404

    if show.total_tickets < num_tickets:
        return jsonify({'message': 'Not enough available tickets'}), 400

    try:
        total_amount = show.ticket_price * num_tickets
        new_booking = Booking(user_id=userid, show_id=show_id, number_of_tickets=num_tickets, total_amount=total_amount, booking_date=datetime.now())
        show.avail_ticket -= num_tickets  # Update the available tickets for the show
        db.session.add(new_booking)
        activity = UserActivity(user_id=userid, activity_type='booking')
        db.session.add(activity)
        db.session.commit()
        return jsonify({'message': 'Ticket booked successfully'}), 200
    except:
        db.session.rollback()
        return jsonify({'message': 'An error occurred while booking the ticket'}), 500


if __name__ == '__main__':
    app.run(debug=True)

    # celery.start()
