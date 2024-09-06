import uuid
from datetime import datetime, timezone
from app.extensions import db
from flask_bcrypt import generate_password_hash, check_password_hash
from werkzeug.security import generate_password_hash, check_password_hash


class User(db.Model):
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)

    def __init__(self, username, password):
        self.username = username
        self.set_password(password)  # Postavljanje hešovane lozinke

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)  # Kreiranje heša od lozinke

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)  # Provera lozinke


class Task(db.Model):
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    title = db.Column(db.String(120), nullable=False)
    body = db.Column(db.Text, nullable=True)
    tag = db.Column(db.String(36), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False, default=datetime.now(timezone.utc))
    end_time = db.Column(db.DateTime, nullable=False)

    def __init__(self, title, tag, user_id, body=None, start_time=None, end_time=None):
        self.title = title  # Naslov zadatka
        self.body = body  # Tekstualni opis zadatka
        self.tag = tag  # Oznaka zadatka
        self.user_id = user_id  # ID korisnika koji je kreirao zadatak
        self.start_time = start_time or datetime.now(timezone.utc)  # Početno vreme zadatka
        self.end_time = end_time  # Krajnje vreme zadatka
        self.start_time = start_time or datetime.now(timezone.utc)  # Početno vreme zadatka

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'body': self.body,
            'tag': self.tag,
            'user_id': self.user_id,
            'start_time': self.start_time,
            'end_time': self.end_time
        }  # Konverzija zadatka u rečnik (dictionary) format
