from flask import Flask, request, jsonify, make_response
from models import *
from flask_security import Security, SQLAlchemyUserDatastore, login_user, roles_accepted, current_user, logout_user
import bcrypt
import secrets

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///./ticket_db.sqlite3'
app.config['SECRET_KEY'] = 'your-secret-key'
app.config['SECURITY_PASSWORD_HASH'] = 'bcrypt'
app.config['SECURITY_PASSWORD_SALT'] = secrets.SystemRandom().getrandbits(128)


db.init_app(app)
app.app_context().push()

user_datastore = SQLAlchemyUserDatastore(db, User, Role)
security=Security(app, user_datastore)

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
    
@app.route('/api/register', methods=['POST'])
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
    
@app.route('/api/login', methods=['POST'])
def loginfn():
    data = request.get_json()
    email = data['email']
    password = data['password']
    user = user_datastore.find_user(email=email)
    # user = User.query.filter_by(email=email).first()
    if user :
        if bcrypt.checkpw(password.encode('utf-8'), user.password):
            # auth_token = user.get_auth_token()
            login_user(user)
            activity = UserActivity(user_id=user.id, activity_type='login')
            db.session.add(activity)
            db.session.commit()
            auth_token = user.get_auth_token()
            return make_response(jsonify({'message': 'User logged in successfully', 'auth_token': auth_token, 'id': current_user.id,
        'email': current_user.email,
        'roles': [role.name for role in current_user.roles]}), 200)
    else:
        return make_response(jsonify({'message': 'Invalid email or password.'}), 400)



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
    app.run(debug=True)