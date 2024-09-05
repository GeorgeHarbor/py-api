from calendar import monthrange
from datetime import datetime, timedelta
from flask import Blueprint, request, jsonify, make_response
from app.models import Task, User
from app.extensions import db
from flask_jwt_extended import jwt_required, get_jwt_identity
import pytz

bp = Blueprint('tasks', __name__, url_prefix='/tasks')


# Utility function to convert UTC to user's timezone
def convert_to_user_timezone(dt, user_timezone):
    try:
        if dt:
            utc = pytz.utc
            user_tz = pytz.timezone(user_timezone)
            return dt.replace(tzinfo=utc).astimezone(user_tz)
        return None
    except pytz.UnknownTimeZoneError:
        return None


# Utility function to convert user's local time to UTC
def convert_to_utc(dt, user_timezone):
    try:
        if dt:
            user_tz = pytz.timezone(user_timezone)
            return user_tz.localize(dt).astimezone(pytz.utc)
        return None
    except pytz.UnknownTimeZoneError:
        return None


# Helper function to convert task times from UTC to user's local timezone and format them
def format_task_times(tasks, user_timezone):
    formatted_tasks = []
    for task in tasks:
        task_dict = task.to_dict()
        task_dict['start_time'] = convert_to_user_timezone(task.start_time, user_timezone).strftime('%Y-%m-%d %H:%M:%S')
        if task.end_time:
            task_dict['end_time'] = convert_to_user_timezone(task.end_time, user_timezone).strftime('%Y-%m-%d %H:%M:%S')
        formatted_tasks.append(task_dict)
    return formatted_tasks


# Helper function to filter tasks by date range and convert from UTC to user's timezone
def get_tasks_in_range(user, start_date, end_date):
    tasks = Task.query.filter(Task.user_id == user.id, Task.start_time >= start_date, Task.end_time <= end_date) \
        .order_by(Task.start_time.asc()).all()
    formatted_tasks = format_task_times(tasks, user.timezone)
    response = jsonify(formatted_tasks)
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '-1'
    return response


@bp.after_request
def add_no_cache_headers(response):
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '-1'
    return response


# Route to get all tasks or filter by date range
@bp.route('/', methods=['GET'])
@jwt_required()
def get_tasks():
    user_id = get_jwt_identity()
    start_time = request.args.get('start_time')
    end_time = request.args.get('end_time')

    user = User.query.get(user_id)

    if start_time and end_time:
        try:
            start_time = datetime.strptime(start_time, '%Y-%m-%d %H:%M:%S')
            end_time = datetime.strptime(end_time, '%Y-%m-%d %H:%M:%S')
            start_time = convert_to_utc(start_time, user.timezone)
            end_time = convert_to_utc(end_time, user.timezone)
        except ValueError:
            response = jsonify({'error': 'Invalid datetime format. Use YYYY-MM-DD HH:MM:SS'})
            return response, 400

        return get_tasks_in_range(user, start_time, end_time)

    tasks = Task.query.filter_by(user_id=user_id).order_by(Task.start_time.asc()).all()
    formatted_tasks = format_task_times(tasks, user.timezone)

    response = jsonify(formatted_tasks)
    return response


# Get tasks for a specific day or today if not provided
@bp.route('/daily', methods=['GET'])
@jwt_required()
def get_daily_tasks():
    user_id = get_jwt_identity()
    date_param = request.args.get('date')

    user = User.query.get(user_id)

    if date_param:
        day = datetime.strptime(date_param, '%Y-%m-%d').date()
    else:
        day = datetime.utcnow().date()

    start_of_day = convert_to_utc(datetime.combine(day, datetime.min.time()), user.timezone)
    end_of_day = convert_to_utc(datetime.combine(day, datetime.max.time()), user.timezone)

    response = get_tasks_in_range(user, start_of_day, end_of_day)
    return response


# Create a task with timezone handling
@bp.route('/', methods=['POST'])
@jwt_required()
def create_task():
    data = request.get_json()
    if not data or 'title' not in data or 'start_time' not in data:
        response = jsonify({'error': 'Title and start_time are required.'})
        return response, 400

    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    try:
        start_time = datetime.strptime(data['start_time'], '%Y-%m-%d %H:%M:%S')
        start_time = convert_to_utc(start_time, user.timezone)
        end_time = None
        if 'end_time' in data:
            end_time = datetime.strptime(data['end_time'], '%Y-%m-%d %H:%M:%S')
            end_time = convert_to_utc(end_time, user.timezone)
        task = Task(
            title=data['title'],
            user_id=user_id,
            start_time=start_time,
            end_time=end_time
        )
        db.session.add(task)
        db.session.commit()
        response = jsonify({'message': 'Task created successfully'})
        return response, 201
    except ValueError:
        response = jsonify({'error': 'Invalid datetime format. Use YYYY-MM-DD HH:MM:SS'})
        return response, 400


# Update a task and handle timezone conversion
@bp.route('/<string:id>', methods=['PUT'])
@jwt_required()
def update_task(id):
    task = Task.query.get_or_404(id)
    data = request.get_json()
    if 'title' in data:
        task.title = data['title']
    db.session.commit()
    response = jsonify({'message': 'Task updated successfully'})
    return response


# Delete a task
@bp.route('/<string:id>', methods=['DELETE'])
@jwt_required()
def delete_task(id):
    task = Task.query.get_or_404(id)
    db.session.delete(task)
    db.session.commit()
    response = jsonify({'message': 'Task deleted successfully'})
    return response
