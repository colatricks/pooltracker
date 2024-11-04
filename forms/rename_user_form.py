from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import InputRequired, Length, Regexp
from better_profanity import profanity

class RenameUserForm(FlaskForm):
    new_username = StringField('New Username', validators=[
        InputRequired(),
        Length(min=3, max=25),
        Regexp('^[A-Za-z][A-Za-z0-9_]*$', message="Username must start with a letter and contain only letters, numbers, and underscores.")
    ])
    submit = SubmitField('Rename')

    def validate_new_username(self, field):
        normalized_username = field.data
        # Check for profanity
        if profanity.contains_profanity(normalized_username):
            raise ValidationError('Username contains inappropriate content. Please choose a different username.')