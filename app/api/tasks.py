from datetime import timezone

from flask import Blueprint, request, jsonify
from app.models import Task, User
from app.extensions import db
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime, timedelta, date

bp = Blueprint('tasks', __name__, url_prefix='/tasks')


# Pomoćna funkcija za filtriranje zadataka po datumskom opsegu
def get_tasks_in_range(user, start_time, end_time):
    tasks = Task.query.filter(Task.user_id == user.id, Task.start_time >= start_time, Task.end_time <= end_time) \
        .order_by(Task.start_time.asc()).all()
    return tasks


# Ruta za dobijanje svih zadataka ili filtriranje po id-u
@bp.route('/', methods=['GET'])
@jwt_required()
def get_tasks():
    user_id = get_jwt_identity()
    task_id = request.args.get('id')
    if task_id is not None:
        task = Task.query.get(task_id)
        if task is None or task.user_id != user_id:
            return jsonify({'error': 'Task not found or access denied.'}), 404
        tasks_json = task.to_dict()
    else:
        tasks = Task.query.filter_by(user_id=user_id).order_by(Task.start_time.asc()).all()
        tasks_json = [task.to_dict() for task in tasks]
    return jsonify(tasks_json)


# Dobijanje zadataka za određeni dan ili za tekući dan ako nije naveden
@bp.route('/daily', methods=['GET'])
@jwt_required()
def get_daily_tasks():
    user_id = get_jwt_identity()
    date_param = request.args.get('date')
    user = User.query.get(user_id)

    if date_param:
        start_of_day = f"{date_param} 00:00:00"
        end_of_day = f"{date_param} 23:59:59"
    else:
        current_date = datetime.today().strftime('%Y-%m-%d')
        start_of_day = f"{current_date} 00:00:00"
        end_of_day = f"{current_date} 23:59:59"

    task_list = Task.query.filter(Task.user_id == user.id, Task.start_time >= start_of_day, Task.end_time <= end_of_day)

    task_dict = [task.to_dict() for task in task_list]
    return jsonify(task_dict)


# Dobijanje zadataka za tekuću nedelju
@bp.route('/weekly', methods=['GET'])
@jwt_required()
def get_weekly_tasks():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    date_str = request.args.get('date')
    if date_str is None:
        date_str = datetime.now().strftime('%Y-%m-%d')
    try:
        start_date = datetime.strptime(date_str, '%Y-%m-%d')
    except ValueError:
        return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD'}), 400

    start_of_week = start_date - timedelta(days=start_date.weekday())
    end_of_week = start_of_week + timedelta(days=6)

    tasks = get_tasks_in_range(user, start_of_week, end_of_week)
    tasks_json = [task.to_dict() for task in tasks]
    return jsonify(tasks_json), 200


# Dobijanje zadataka za tekući mesec
@bp.route('monthly', methods=['GET'])
@jwt_required()
def get_monthly_tasks():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    data_str = request.args.get('date')

    if data_str:
        start_of_month = datetime.strptime(data_str, '%Y-%m-%d').replace(day=1)
    else:
        start_of_month = datetime.today().replace(day=1)

    next_month = start_of_month.replace(day=28) + timedelta(days=4)  # ovo nikada neće zakačiti
    end_of_month = next_month - timedelta(days=next_month.day)

    tasks = get_tasks_in_range(user, start_of_month, end_of_month)
    tasks_json = [task.to_dict() for task in tasks]
    return jsonify(tasks_json), 200


# Dobijanje zadataka za određeni vremenski opseg
@bp.route('/range', methods=['GET'])
@jwt_required()
def tasks_in_range():
    user_id = get_jwt_identity()
    start_time = request.args.get('start_time')
    end_time = request.args.get('end_time')

    if not start_time or not end_time:
        return jsonify({'error': 'Both start_time and end_time are required.'}), 400

    try:
        start_time = datetime.fromisoformat(start_time)
        end_time = datetime.fromisoformat(end_time)
    except ValueError:
        return jsonify({'error': 'Invalid datetime format. Use YYYY-MM-DD HH:MM:SS'}), 400

    user = User.query.get_or_404(user_id)
    tasks = get_tasks_in_range(user, start_time, end_time)

    tasks_json = [task.to_dict() for task in tasks]
    return jsonify(tasks_json), 200


# Kreiranje zadatka
@bp.route('/', methods=['POST'])
@jwt_required()
def create_task():
    data = request.get_json()
    if not data or 'title' not in data or 'start_time' not in data:
        response = jsonify({'error': 'Title and start_time are required.'})
        return response, 400

    try:
        start_time = datetime.fromisoformat(data['start_time'])
        end_time = datetime.fromisoformat(data['end_time']) if 'end_time' in data else None
    except ValueError:
        return jsonify({'error': 'Invalid datetime format. Use YYYY-MM-DD HH:MM:SS'}), 400

    user_id = get_jwt_identity()

    task = Task(
        title=data['title'],
        tag=data['tag'],
        user_id=user_id,
        body=data.get('body'),
        start_time=start_time,
        end_time=end_time
    )
    db.session.add(task)
    db.session.commit()
    return jsonify(task.to_dict()), 201


# Ažuriranje zadatka
@bp.route('/', methods=['PUT'])
@jwt_required()
def update_task():
    id = request.args.get('id')
    task = Task.query.get_or_404(id)
    data = request.get_json()
    if 'title' in data:
        task.title = data['title']
    db.session.commit()

    task.query.get_or_404(id)
    return jsonify(task.to_dict())


# Brisanje zadatka
@bp.route('/', methods=['DELETE'])
@jwt_required()
def delete_task():
    id = request.args.get('id')
    task = Task.query.get_or_404(id)
    db.session.delete(task)
    db.session.commit()
    return jsonify({'message': 'Task deleted successfully'})
