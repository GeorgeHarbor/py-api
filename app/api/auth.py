from flask import Blueprint, request, jsonify
from app.models import User
from app.extensions import db
from flask_jwt_extended import create_access_token

bp = Blueprint('auth', __name__, url_prefix='/auth')


@bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()  # Preuzimanje podataka iz POST zahteva
    username = data['username']  # Dohvatanje korisničkog imena
    password = data['password']  # Dohvatanje lozinke

    user = User(username=username, password=password)  # Kreiranje novog korisnika
    db.session.add(user)  # Dodavanje korisnika u sesiju
    db.session.commit()  # Čuvanje korisnika u bazi podataka

    return jsonify({'message': 'User registered successfully'}), 201  # Odgovor sa statusnim kodom 201


@bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()  # Preuzimanje podataka iz POST zahteva
    user = User.query.filter_by(username=data['username']).first()  # Pretraga korisnika po korisničkom imenu
    if user and user.check_password(data['password']):  # Provera lozinke
        access_token = create_access_token(identity=user.id)  # Kreiranje JWT token-a
        return jsonify({'access_token': access_token}), 200  # Odgovor sa statusnim kodom 200
    return jsonify({'message': 'Invalid credentials'}), 401  # Odgovor sa statusnim kodom 401
