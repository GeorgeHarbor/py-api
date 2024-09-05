import uuid
from datetime import datetime

from app.extensions import db
from flask_bcrypt import generate_password_hash, check_password_hash

class User(db.Model):
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    timezone = db.Column(db.String(50), nullable=False)

    def set_username(self, username):
        self.username = username
    def set_password(self, password):
        self.password_hash = generate_password_hash(password).decode('utf8')
    def set_timezone(self, timezone):
        self.timezone = timezone

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

import uuid
from app.extensions import db

class Task(db.Model):
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    title = db.Column(db.String(120), nullable=False)
    body = db.Column(db.Text, nullable=True)
    tag = db.Column(db.String(36), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False, default=datetime.utcnow())
    end_time = db.Column(db.DateTime, nullable=True)

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'body': self.body,
            'tag': self.tag,
            'user_id': self.user_id,
            'start_time': self.start_time,
            'end_time': self.end_time
        }
