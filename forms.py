from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField
from wtforms.validators import DataRequired, Length, ValidationError
from models import User

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(message='A felhasználónév megadása kötelező')])
    password = PasswordField('Password', validators=[DataRequired(message='A jelszó megadása kötelező')])
    remember_me = BooleanField('Emlékezz rám')

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[
        DataRequired(message='A felhasználónév megadása kötelező'),
        Length(min=4, max=64, message='A felhasználónévnek 4 és 64 karakter között kell lennie')
    ])
    
    password = PasswordField('Password', validators=[
        DataRequired(message='A jelszó megadása kötelező'),
        Length(min=4, message='A jelszónak legalább 4 karakter hosszúnak kell lennie')
    ])
    
    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Kérjük, használj más felhasználónevet, ez már foglalt.')
