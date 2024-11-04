from flask_wtf import FlaskForm
from wtforms import SelectField, SubmitField, RadioField
from wtforms.validators import InputRequired, ValidationError
from models.user import User

class NewGameForm(FlaskForm):
    player1 = SelectField('Player A', validators=[InputRequired()], coerce=int)
    player2 = SelectField('Player B', validators=[InputRequired()], coerce=int)
    winner = RadioField('Winner', validators=[InputRequired()], coerce=int)
    submit = SubmitField("Record Game!")

    def validate(self, *args, **kwargs):
        if not super(NewGameForm, self).validate(*args, **kwargs):
            return False
        if self.player1.data == self.player2.data:
            self.player2.errors.append("Player A and Player B cannot be the same.")
            return False
        # Ensure the winner is one of the selected players
        if self.winner.data not in [self.player1.data, self.player2.data]:
            self.winner.errors.append("Winner must be either Player A or Player B.")
            return False
        return True
