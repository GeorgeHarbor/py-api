from datetime import datetime

from flask import Blueprint, request, jsonify
from app.models import Task
from app.extensions import db
from flask_jwt_extended import jwt_required, get_jwt_identity

bp = Blueprint('tasks', __name__, url_prefix='/tasks')

@bp.route('/', methods=['GET'])
@jwt_required()
def get_tasks():
    user_id = get_jwt_identity()
    tasks = Task.query.filter_by(user_id=user_id).all()
    return jsonify([task.to_dict() for task in tasks])

@bp.route('/', methods=['POST'])
@jwt_required()
def create_task():
    data = request.get_json()
    user_id = get_jwt_identity()
    start_time = datetime.strptime(data['start_time'], '%Y-%m-%d %H:%M:%S') if 'start_time' in data else datetime.utcnow()
    end_time = datetime.strptime(data['end_time'], '%Y-%m-%d %H:%M:%S') if 'end_time' in data else None
    task = Task(
        title=data['title'],
        user_id=user_id,
        start_time=start_time,
        end_time=end_time
    )
    db.session.add(task)
    db.session.commit()

    return jsonify({'message': 'Task created successfully'}), 201

@bp.route('/<int:id>', methods=['PUT'])
@jwt_required()
def update_task(id):
    task = Task.query.get_or_404(id)
    data = request.get_json()
    task.title = data['title']
    db.session.commit()
    return jsonify({'message': 'Task updated successfully'})

@bp.route('/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_task(id):
    task = Task.query.get_or_404(id)
    db.session.delete(task)
    db.session.commit()
    return jsonify({'message': 'Task deleted successfully'})
