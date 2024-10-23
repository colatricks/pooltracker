from flask import Flask, render_template, redirect, url_for, flash, request
from models import User, init_db
from models.game import Game
from forms import RegisterForm, NewGameForm

app = Flask(__name__)
app.config.from_object('config.Config')

# Initialize the database within an application context
with app.app_context():
    init_db()

@app.route('/')
def index():
    return render_template('dashboard.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        user = User.create(form.username.data)
        if user:
            flash(f"Player {user.username} registered successfully.")
            return redirect(url_for('register'))
        else:
            flash("Username already exists.")
    return render_template('register.html', form=form)

@app.route('/dashboard')
def dashboard():
    # Get sorting parameter from URL query string
    sort_by = request.args.get('sort_by', 'win_percentage')
    sort_order = request.args.get('sort_order', 'desc')

    # Fetch player statistics
    players = User.get_player_statistics()

    # Sort players based on selected column and order
    reverse = True if sort_order == 'desc' else False
    if sort_by == 'wins':
        players.sort(key=lambda x: x['wins'], reverse=reverse)
    elif sort_by == 'losses':
        players.sort(key=lambda x: x['losses'], reverse=reverse)
    elif sort_by == 'win_percentage':
        players.sort(key=lambda x: x['win_percentage'], reverse=reverse)
    else:
        # Default sorting by username
        players.sort(key=lambda x: x['username'])

    # Get top 10 players
    top_players = players[:10]

    # Fetch all games for the rolling results table
    games = Game.get_all_games()

    return render_template('dashboard.html', games=games, top_players=top_players, sort_by=sort_by, sort_order=sort_order)


@app.route('/new_game', methods=['GET', 'POST'])
def new_game():
    form = NewGameForm()
    # Populate the player choices
    players = User.get_all_users()
    form.player1.choices = [(player.id, player.username) for player in players]
    form.player2.choices = [(player.id, player.username) for player in players]
    
    # Determine if players are selected to set winner choices
    if form.player1.data and form.player2.data and form.player1.data != form.player2.data:
        form.winner.choices = [
            (form.player1.data, dict(form.player1.choices).get(form.player1.data)),
            (form.player2.data, dict(form.player2.choices).get(form.player2.data))
        ]
    else:
        form.winner.choices = []

    if form.validate_on_submit():
        Game.record_game(
            form.player1.data,
            form.player2.data,
            form.winner.data
        )
        flash("Game recorded successfully.")
        return redirect(url_for('dashboard'))
    return render_template('new_game.html', form=form)


@app.route('/rules')
def rules():
    return render_template('rules.html')

if __name__ == '__main__':
    with app.app_context():
        init_db(app.config['DATABASE'])
    app.run(debug=True)