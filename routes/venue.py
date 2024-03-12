from flask import jsonify, request, make_response
from models import *
# from security_framework import roles_accepted, auth_token_required
from flask_security import roles_accepted, auth_token_required
from flask_restful import Resource
#/api/venues
class all_venue(Resource):
    def get(self):
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
    
    @roles_accepted('admin')
    @auth_token_required
    def post(self):
        data = request.get_json()
        name = data['name']
        address = data['address']
        capacity = data['capacity']
        description = data['description']
        venue = Venue(name=name, address=address, capacity=capacity, description=description)
        db.session.add(venue)
        db.session.commit()
        return make_response(jsonify({'message': 'Venue has been added successfully'}), 200)



#/api/venues/<int:venue_id>
class venue(Resource):
    def get(self, venue_id):
        venue = Venue.query.get(venue_id)
        if not venue:
            return make_response(jsonify({'message': 'Venue not found'}), 404)
        venue_info = {
            'id': venue.id,
            'name': venue.name,
            'address': venue.address,
            'capacity': venue.capacity,
            'description': venue.description,
        }
        return make_response(jsonify(venue_info), 200)
    
    @auth_token_required
    @roles_accepted('admin', 'user')
    def put(self, venue_id):
        venue = Venue.query.get(venue_id)
        if not venue: # if not venue and if venue.who_created != current_user.id:
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
    
    def delete(self, venue_id):
        venue = Venue.query.get(venue_id)
        if not venue:
            return make_response(jsonify({'message': 'Venue not found'}), 404)
        db.session.delete(venue)
        db.session.commit()
        return make_response(jsonify({'message': 'Venue deleted successfully'}), 200)