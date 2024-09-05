import pytz
from flask import Blueprint, request, jsonify
from app.models import User
from app.extensions import db
from flask_jwt_extended import create_access_token

bp = Blueprint('auth', __name__, url_prefix='/auth')


@bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data['username']
    password = data['password']
    timezone = data['timezone']  # Ensure user provides timezone

    # Validate the timezone here
    try:
        pytz.timezone(timezone)  # Will raise an exception if the timezone is invalid
    except pytz.UnknownTimeZoneError:
        return jsonify({'error': 'Invalid timezone provided'}), 400

    user = User()
    user.set_username(username)
    user.set_password(password)
    user.set_timezone(timezone)
    db.session.add(user)
    db.session.commit()

    return jsonify({'message': 'User registered successfully'}), 201


@bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    user = User.query.filter_by(username=data['username']).first()
    if user and user.check_password(data['password']):
        access_token = create_access_token(identity=user.id)
        return jsonify({'access_token': access_token}), 200
    return jsonify({'message': 'Invalid credentials'}), 401
