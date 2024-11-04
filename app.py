from flask import Flask, render_template, redirect, url_for, flash, request, session
from models import User, init_db
from models.game import Game
from forms import RegisterForm, NewGameForm
from models.user import User
from forms.rename_user_form import RenameUserForm
from functools import wraps

app = Flask(__name__)
app.config.from_object('config.Config')

# Simple admin authentication
ADMIN_PASSWORD = 'adminpassword'  # Replace with a secure password

# Initialize the database within an application context
with app.app_context():
    init_db()

def is_admin():
    return session.get('is_admin', False)

@app.context_processor
def inject_is_admin():
    return dict(is_admin=is_admin)

@app.route('/admin_login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        password = request.form.get('password')
        if password == ADMIN_PASSWORD:
            session['is_admin'] = True
            return redirect(url_for('admin'))
        else:
            flash('Invalid password.')
    return render_template('admin_login.html')

@app.route('/admin_logout')
def admin_logout():
    session.pop('is_admin', None)
    return redirect(url_for('index'))

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not is_admin():
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def index():
    return render_template('dashboard.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        normalized_username = User.normalize_username(form.username.data)
        new_user = User.create(normalized_username)
        if new_user:
            flash('User registered successfully.')
            return redirect(url_for('index'))
        else:
            form.username.errors.append('Username is already taken. Please choose a different one.')
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

@app.route('/admin')
@admin_required
def admin():
    users = User.get_all_users()
    return render_template('admin.html', users=users)

@app.route('/delete_user/<int:user_id>', methods=['POST'])
@admin_required
def delete_user(user_id):
    user = User.get_by_id(user_id)
    if user:
        User.delete(user_id)
        flash(f'User {user.username} and all associated games have been deleted.')
    else:
        flash('User not found.')
    return redirect(url_for('admin'))

@app.route('/rename_user/<int:user_id>', methods=['GET', 'POST'])
@admin_required
def rename_user(user_id):
    user = User.get_by_id(user_id)
    if not user:
        flash('User not found.')
        return redirect(url_for('admin'))

    form = RenameUserForm()
    if form.validate_on_submit():
        new_username = form.new_username.data
        # Normalize the username
        normalized_username = User.normalize_username(new_username)
        # Check if the username is already taken
        if User.get_by_username(normalized_username):
            form.new_username.errors.append('Username is already taken. Please choose a different one.')
        else:
            # Update the user's username
            User.update_username(user_id, normalized_username)
            flash(f'User renamed to {normalized_username}.')
            return redirect(url_for('admin'))
    else:
        # Pre-fill the form with the current username
        form.new_username.data = user.username

    return render_template('rename_user.html', form=form, user=user)

if __name__ == '__main__':
    with app.app_context():
        init_db(app.config['DATABASE'])
    app.run(debug=True)