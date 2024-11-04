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
    # Enable foreign key constraints
    cursor.execute('PRAGMA foreign_keys = ON;')
    # Drop the existing tables if they exist
    cursor.execute('DROP TABLE IF EXISTS games')
    cursor.execute('DROP TABLE IF EXISTS users')
    # Recreate the users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL COLLATE NOCASE,
            UNIQUE (username)
        )
    ''')
    # Recreate the games table with ON DELETE CASCADE
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS games (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            player1_id INTEGER NOT NULL,
            player2_id INTEGER NOT NULL,
            winner_id INTEGER NOT NULL,
            date_played DATE DEFAULT (datetime('now','localtime')),
            FOREIGN KEY (player1_id) REFERENCES users (id) ON DELETE CASCADE,
            FOREIGN KEY (player2_id) REFERENCES users (id) ON DELETE CASCADE,
            FOREIGN KEY (winner_id) REFERENCES users (id) ON DELETE CASCADE
        )
    ''')
    conn.commit()
    conn.close()