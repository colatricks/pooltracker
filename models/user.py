from .database import get_db_connection

class User:
    def __init__(self, id_, username):
        self.id = id_
        self.username = username

    @staticmethod
    def get(user_id):
        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()
        conn.close()
        if not user:
            return None
        return User(int(user['id']), user['username'])

    @staticmethod
    def get_by_username(username):
        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
        conn.close()
        if not user:
            return None
        return User(int(user['id']), user['username'])

    @staticmethod
    def create(username):
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('INSERT INTO users (username) VALUES (?)', (username,))
            conn.commit()
            user_id = cursor.lastrowid
        except sqlite3.IntegrityError:
            conn.close()
            return None
        conn.close()
        return User.get(user_id)
    
    @staticmethod
    def get_all_users():
        conn = get_db_connection()
        users = conn.execute('SELECT * FROM users').fetchall()
        conn.close()
        return [User(int(user['id']), user['username']) for user in users]
    
    @staticmethod
    def get_top_players_by_games_played(limit=10):
        conn = get_db_connection()
        players = conn.execute('''
            SELECT users.id, users.username, COUNT(games.id) as games_played
            FROM users
            JOIN games ON users.id = games.player1_id OR users.id = games.player2_id
            GROUP BY users.id
            ORDER BY games_played DESC
            LIMIT ?
        ''', (limit,)).fetchall()
        conn.close()
        return players

    @staticmethod
    def get_top_players_by_games_won(limit=10):
        conn = get_db_connection()
        players = conn.execute('''
            SELECT users.id, users.username, COUNT(games.id) as games_won
            FROM users
            JOIN games ON users.id = games.winner_id
            GROUP BY users.id
            ORDER BY games_won DESC
            LIMIT ?
        ''', (limit,)).fetchall()
        conn.close()
        return players

    @staticmethod
    def get_top_players_by_games_lost(limit=10):
        conn = get_db_connection()
        players = conn.execute('''
            SELECT users.id, users.username, (COUNT(games.id) - COALESCE(wins.games_won, 0)) as games_lost
            FROM users
            JOIN games ON users.id = games.player1_id OR users.id = games.player2_id
            LEFT JOIN (
                SELECT winner_id, COUNT(*) as games_won
                FROM games
                GROUP BY winner_id
            ) wins ON users.id = wins.winner_id
            GROUP BY users.id
            ORDER BY games_lost DESC
            LIMIT ?
        ''', (limit,)).fetchall()
        conn.close()
        return players
    
    @staticmethod
    def get_player_statistics():
        conn = get_db_connection()
        players = conn.execute('''
            SELECT users.id, users.username,
                COALESCE(wins.games_won, 0) as wins,
                (COALESCE(total_games.games_played, 0) - COALESCE(wins.games_won, 0)) as losses,
                CASE
                    WHEN COALESCE(total_games.games_played, 0) > 0 THEN
                        ROUND((CAST(COALESCE(wins.games_won, 0) AS FLOAT) / COALESCE(total_games.games_played, 0)) * 100, 2)
                    ELSE 0
                END as win_percentage
            FROM users
            LEFT JOIN (
                SELECT winner_id, COUNT(*) as games_won
                FROM games
                GROUP BY winner_id
            ) wins ON users.id = wins.winner_id
            LEFT JOIN (
                SELECT users.id as user_id, COUNT(games.id) as games_played
                FROM users
                LEFT JOIN games ON users.id = games.player1_id OR users.id = games.player2_id
                GROUP BY users.id
            ) total_games ON users.id = total_games.user_id
            ORDER BY users.username ASC
        ''').fetchall()
        conn.close()
        return players