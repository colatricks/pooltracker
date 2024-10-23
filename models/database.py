from flask import current_app
import sqlite3

DATABASE = 'pool_score_tracker.db'

def get_db_connection():
    conn = sqlite3.connect(current_app.config['DATABASE'])
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    # Drop the existing tables if they exist (be cautious with this in production)
    cursor.execute('DROP TABLE IF EXISTS users')
    cursor.execute('DROP TABLE IF EXISTS games')
    # Recreate the users table
    cursor.execute('''CREATE TABLE users (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        username TEXT UNIQUE NOT NULL
                      )''')
    # Recreate the games table with the updated schema
    cursor.execute('''CREATE TABLE games (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        player1_id INTEGER NOT NULL,
                        player2_id INTEGER NOT NULL,
                        winner_id INTEGER NOT NULL,
                        date_played DATE DEFAULT (datetime('now','localtime')),
                        FOREIGN KEY (player1_id) REFERENCES users (id),
                        FOREIGN KEY (player2_id) REFERENCES users (id),
                        FOREIGN KEY (winner_id) REFERENCES users (id)
                      )''')
    conn.commit()
    conn.close()