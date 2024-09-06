import os

# Dobij osnovni direktorijum za projekat (dva nivoa iznad lokacije config.py)
basedir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))


class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-key')  # TAJNI KLJUČ
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'database.db')  # Povezivanje baze podataka
    SQLALCHEMY_TRACK_MODIFICATIONS = False  # Prati modifikacije u SQLAlchemy
    JWT_SECRET_KEY = 'your-jwt-secret-key'  # TAJNI KLJUČ za JWT
    JWT_ACCESS_TOKEN_EXPIRES = False  # Tokeni ne ističu
