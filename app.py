from flask import Flask, request, jsonify, make_response
from models import *
from security_framework import login_user, roles_accepted, current_user, logout_user, security, user_datastore
import bcrypt, secrets
from flask_cors import CORS
from flask_restful import Api
from flask_security import auth_token_required

import os

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///./ticket_db.sqlite3'
app.config['SECRET_KEY'] = 'your-secret-key'
app.config['SECURITY_PASSWORD_HASH'] = 'bcrypt'
app.config['SECURITY_PASSWORD_SALT'] = secrets.SystemRandom().getrandbits(128)
app.config['SECURITY_TRACKABLE'] = True

def create_api_app():
    api = Api(app)
    app.app_context().push()
    print('api created')
    return api

db.init_app(app)
app.app_context().push()

api_hanlder = create_api_app()
CORS(app)

# user_datastore = SQLAlchemyUserDatastore(db, User, Role)
# security=Security(app, user_datastore)

security.init_app(app, user_datastore)

# Function to create roles
def create_roles():
    # Define roles and their permissions
    roles_permissions = {
        'admin': 'admin-access',
        'user': 'user-access',
    }
    # Iterate over each role
    for role_name, role_permissions in roles_permissions.items():
        # Check if the role already exists
        role = Role.query.filter_by(name=role_name).first()
        # If the role does not exist, create it
        if not role:
            role = Role(name=role_name, description=role_permissions)
            # Add the new role to the session
            db.session.add(role)
    # Commit the session to save the changes
    db.session.commit()

# Function to create an admin user
def admin_user_creation():
    # Get the admin role
    admin_role = Role.query.filter_by(name='admin').first()
    # Check if there is already a user with the admin role
    admin_user = User.query.filter(User.roles.any(id=admin_role.id)).first()

    # If there is no admin user, create one
    if not admin_user:
        # Define the admin email and password
        admin_email = 'admin@abc.com'  # Change this email as needed
        admin_password = 'admin'
        # Hash the password
        hashed_password = bcrypt.hashpw(admin_password.encode('utf-8'), bcrypt.gensalt())

        # Create the admin user
        admin_user = user_datastore.create_user(email=admin_email, password=hashed_password)
        # Add the admin role to the user
        user_datastore.add_role_to_user(admin_user, 'admin')
        # user_datastore.add_role_to_user(genral_user, 'user')

        # Commit the session to save the changes
        db.session.commit()
        return True
    return False


@app.route('/', methods=['GET', 'POST'])
# check if the request contains a token or not, if yes then we validate the token and return the user details
def hello_world():
    if request.method == 'GET':
        var1 = 'my function'
        var2 = 1+2
        return make_response(jsonify({'json_var1': var1, 'json_var2': var2}), 200)
    if request.method == 'POST':
        data = request.get_json()
        name = data['var3']
        address = data['var4']
        print(name, address)
        return make_response(jsonify({'message':'THE JSON WAS CAPTURED'}), 200)
    
@app.route('/apis/register', methods=['POST'])
def registerfn():
    data = request.get_json()
    email = data['email']
    password = data['password']
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    try:
        general_user = user_datastore.create_user(email=email, password=hashed_password)
        user_datastore.add_role_to_user(general_user, 'user')
        db.session.commit()
        user_id = User.query.filter_by(email=email).first().id
        activity = UserActivity(user_id=user_id, activity_type='registered')
        db.session.add(activity)
        db.session.commit()
        return make_response(jsonify({'message': 'User has been registered successfully'}), 200)
    except:
        # Handle the case when the email already exists
        return make_response(jsonify({'message': 'This email is already registered. Please use a different email.'}), 400)    
    
@app.route('/apis/login', methods=['POST'])
def loginfn():
    data = request.get_json()
    email = data['email']
    password = data['password']
    user = user_datastore.find_user(email=email)
    # user = User.query.filter_by(email=email).first()
    if user :
        if bcrypt.checkpw(password.encode('utf-8'), user.password):
            # auth_token = user.get_auth_token()
            login_user(user) # session based login
            activity = UserActivity(user_id=user.id, activity_type='login')
            db.session.add(activity)
            db.session.commit()
            auth_token = user.get_auth_token() # token based login
            return make_response(jsonify({'message': 'User logged in successfully', 'auth_token': auth_token, 'id': current_user.id,
        'email': current_user.email,
        'roles': [role.name for role in current_user.roles]}), 200)
    else:
        return make_response(jsonify({'message': 'Invalid email or password.'}), 400)

@app.route('/apis/venues', methods=['GET','POST'])
def venuefns():
    if request.method == 'GET':
        venues = Venue.query.all()
        print(venues)
        
        venue_data = []
        for venue in venues:
            venue_info = {
                'id': venue.id,
                'name': venue.name,
                'address': venue.address,
                'capacity': venue.capacity,
                'description': venue.description,
            }

            venue_data.append(venue_info)
        return make_response(jsonify(venue_data), 200)
        
        # return make_response(jsonify([venue.search() for venue in venues]), 200)
    if request.method == 'POST':
        data = request.get_json()
        name = data['name']
        address = data['address']
        capacity = data['capacity']
        description = data['description']
        venue = Venue(name=name, address=address, capacity=capacity, description=description)
        db.session.add(venue)
        db.session.commit()
        return make_response(jsonify({'message': 'Venue has been added successfully'}), 200)

@app.route('/apis/venues/<int:venue_id>', methods=['GET', 'PUT', 'DELETE'])    
def venuefn(venue_id):    
    if request.method == 'PUT':
        venue = Venue.query.get(venue_id)
        if not venue:
            return make_response(jsonify({'message': 'Venue not found'}), 404)
        data = request.get_json()
        capacity = data.get('capacity')
        description = data.get('description')
        name = data['name']
        address = data['address']

        if capacity is not None:
            venue.capacity = capacity
        if description is not None:
            venue.description = description

        db.session.commit()
        return make_response(jsonify({'message': 'Venue updated successfully'}), 200)
    
    if request.method == 'DELETE':
        venue = Venue.query.get(venue_id)
        if not venue:
            return make_response(jsonify({'message': 'Venue not found'}), 404)
        db.session.delete(venue)
        db.session.commit()
        return make_response(jsonify({'message': 'Venue deleted successfully'}), 200)
    
    if request.method == 'GET':
        venue = Venue.query.get(venue_id)
        if not venue:
            return make_response(jsonify({'message': 'Venue not found'}), 404)
        return make_response(jsonify(venue.search()), 200)

@app.route('/test_data', methods=['GET'])
def all_data():
    venues = Venue.query.all()
    print(venues)
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
        # for show in shows:
        #     if show.venue_id == venue.id:
        #         show_info = {
        #             'id': show.id,
        #             'name': show.name,
        #             'description': show.description,
        #             'rating': show.rating,
        #             'tags': show.tags,
        #             'ticket_price': show.ticket_price,
        #             'total_tickets': show.total_tickets,
        #             'avialable_tickets': show.avail_ticket,
        #         }
        #         venue_info['shows'].append(show_info)
        venues_data.append(venue_info)

    return make_response(jsonify(venues_data), 200)

from flask import redirect, url_for
@app.route('/error')
def error():
    user = User.query.first()
    # ebook = Ebook.query.filter_by(id=1).first()
    var = 'static/test.jpg' # ebook.file_path
    return make_response(jsonify({"path":var}), 200)
    # return redirect(url_for('all_data'))

from routes.auth import *
# api.add_resource(login, '/api/login')
api_hanlder.add_resource(logout, '/api/logout')
api_hanlder.add_resource(test_register, '/api/register')

from routes.venue import *
api_hanlder.add_resource(all_venue, '/api/venues')
api_hanlder.add_resource(venue, '/api/venues/<int:venue_id>')

from routes.all_data import *
api_hanlder.add_resource(VenueShow, '/venues-and-shows')

'''
@app.route('/usesrr_login', methods=['GET', 'POST'])


@app.route('/test', methods=['GET', 'POST'])
def test():
    var = user.query.all()
    print(var)
    return render_template('test.html', jinja_var=var)
'''

if __name__ == '__main__':
    db.create_all()
    create_roles()
    admin_user_creation()
    app.run(debug=True, port=6000)