from flask_sqlalchemy import SQLAlchemy
from flask_security import UserMixin, RoleMixin
from datetime import datetime, timedelta

db = SQLAlchemy()

roles_users = db.Table(
    'roles_users',
    db.Column('user_id', db.Integer(), db.ForeignKey('user.id')),
    db.Column('role_id', db.Integer(), db.ForeignKey('role.id'))
)

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True)
    password = db.Column(db.String(255))
    active = db.Column(db.Boolean())
    # confirmed_at = db.Column(db.DateTime())
    fs_uniquifier = db.Column(db.String(64), unique=True)
    roles = db.relationship('Role', secondary=roles_users, backref=db.backref('users', lazy='dynamic'))

class Role(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    description = db.Column(db.String(255))
    permissions = db.Column(db.String(255))
    def get_permissions(self):
        if self.permissions:
            return self.permissions.split(',')
        else:
            return []
#___________________________________________________________________________________________________________#

class Venue(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    address = db.Column(db.String(), nullable=False)
    capacity = db.Column(db.Integer, nullable=False)
    description = db.Column(db.String())
    def serialize(self):
        return {
            'id': self.id,
            'name': self.name,
            'address': self.address,
            'capacity': self.capacity,
            'description': self.description
        }
class Show(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    description = db.Column(db.Text())
    tags = db.Column(db.String(255))
    rating = db.Column(db.Float())
    ticket_price = db.Column(db.Float())
    total_tickets = db.Column(db.Integer())
    avail_ticket = db.Column(db.Integer())
    venue_id = db.Column(db.Integer, db.ForeignKey('venue.id'))
    def serialize(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'tags': self.tags,
            'rating': self.rating,
            'ticket_price': self.ticket_price,
            'total_tickets': self.total_tickets,
            'avail_ticket': self.avail_ticket,
            'venue_id': self.venue_id
        }

class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True) 
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    show_id = db.Column(db.Integer, db.ForeignKey('show.id'))
    booking_date = db.Column(db.DateTime())
    number_of_tickets = db.Column(db.Integer())
    total_amount = db.Column(db.Float())
    booked_tickets = db.Column(db.Integer())

class UserActivity(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    activity_type = db.Column(db.String(50), nullable=False)  # e.g., "login", "visit", etc.
    activity_timestamp = db.Column(db.DateTime, default=datetime.utcnow)