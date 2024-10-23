from .database import get_db_connection

class Game:
    @staticmethod
    def record_game(player1_id, player2_id, winner_id):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO games (player1_id, player2_id, winner_id)
            VALUES (?, ?, ?)
        ''', (player1_id, player2_id, winner_id))
        conn.commit()
        conn.close()

    @staticmethod
    def get_all_games():
        conn = get_db_connection()
        games = conn.execute('''
            SELECT games.*, 
                   u1.username AS player1_name, 
                   u2.username AS player2_name,
                   uw.username AS winner_name
            FROM games
            JOIN users u1 ON games.player1_id = u1.id
            JOIN users u2 ON games.player2_id = u2.id
            JOIN users uw ON games.winner_id = uw.id
            ORDER BY date_played DESC
        ''').fetchall()
        conn.close()
        return games
