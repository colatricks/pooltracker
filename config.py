import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your_secret_key'
    DATABASE = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'pool_score_tracker.db')
