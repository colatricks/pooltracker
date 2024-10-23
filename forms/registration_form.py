from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import InputRequired, Length, ValidationError
from models.user import User

class RegisterForm(FlaskForm):
    username = StringField(
        validators=[InputRequired(), Length(min=2, max=20)],
        render_kw={"placeholder": "Username"}
    )
    submit = SubmitField("Register")

    def validate_username(self, username):
        existing_user = User.get_by_username(username.data)
        if existing_user:
            raise ValidationError("Username already exists. Choose a different one.")
