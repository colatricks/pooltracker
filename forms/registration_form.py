from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import InputRequired, Length, Regexp, ValidationError
from models.user import User
from better_profanity import profanity

class RegisterForm(FlaskForm):
    username = StringField('Username', validators=[
        InputRequired(),
        Length(min=3, max=25),
        Regexp('^[A-Za-z][A-Za-z0-9_]*$', message="Username must start with a letter and contain only letters, numbers, and underscores.")
    ])
    submit = SubmitField('Register')

    def validate_username(self, field):
        normalized_username = User.normalize_username(field.data)

        # Initialize the profanity filter (optional)
        profanity.load_censor_words()  # Load default profanity list

        # Check for profanity
        if profanity.contains_profanity(normalized_username):
            raise ValidationError('Username contains inappropriate content. Please choose a different username.')

        # Check for existing username
        if User.get_by_username(normalized_username):
            raise ValidationError('Username is already taken. Please choose a different one.')