from flask_login import UserMixin
from werkzeug.security import generate_password_hash,check_password_hash
from extensions import db #make sure this points to your actual db instance



class User(db.Model, UserMixin):
    id=db.Column(db.Integer, primary_key=True)
    username=db.Column(db.String(64), unique=True, nullable=False)
    password_hash=db.Column(db.String(128), nullable=False)
    role=db.Column(db.String(10), default='user', nullable=False)

    #Write only
    @property
    def password(self):
        raise AttributeError("Password is write-only")

    @password.setter
    def password(self, password):
        self.password_hash=generate_password_hash(password)

    def check_password(self, password):
            return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.username}>'

    def to_dict(self):
        return {
            "id": self.id, 
            "username": self.username,
            "role": self.role,
        }
#fixed indentation, functions outside class :>
