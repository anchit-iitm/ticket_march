from flask import jsonify, request, make_response
from models import *
from security_framework import user_datastore, bcrypt, login_user, roles_accepted, current_user, logout_user
from flask_restful import Resource
from flask_security import auth_token_required
# from app import user_datastore

class test_register(Resource):
    def post(self):
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

    def get(self):
        return make_response(jsonify({'message': 'This is a get response from the register class'}), 400)  
    

class logout(Resource):
    def post(self):
        activity = UserActivity(user_id=current_user.id, activity_type='logout')
        db.session.add(activity)
        db.session.commit()
        if current_user.is_authenicated:
            logout_user()
            return make_response(jsonify({'message': 'User has been logged out successfully'}), 200)
        return make_response(jsonify({'message': 'User is not logged in'}), 300)