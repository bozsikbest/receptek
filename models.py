from app import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from enum import Enum

class UserRole(Enum):
    USER = 'user'
    ADMIN = 'admin'

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    password_hash = db.Column(db.String(256))
    role = db.Column(db.String(20), nullable=False, default=UserRole.USER.value)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def is_admin(self):
        return self.role == UserRole.ADMIN.value

class Recipe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    ingredients = db.Column(db.Text, nullable=False)
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', backref=db.backref('recipes', lazy=True))

    def __init__(self, name, ingredients, content, user_id):
        self.name = name
        self.ingredients = ','.join(ingredients)
        self.content = content
        self.user_id = user_id

    def get_ingredients(self):
        return self.ingredients.split(',') if self.ingredients else []

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'ingredients': self.get_ingredients(),
            'content': self.content
        }