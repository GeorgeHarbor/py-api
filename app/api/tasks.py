from calendar import calendar
from datetime import datetime, timedelta
from flask import Blueprint, request, jsonify
from app.models import Task, User  # Assuming User and Task models exist
from app.extensions import db
from flask_jwt_extended import jwt_required, get_jwt_identity
import pytz

bp = Blueprint('tasks', __name__, url_prefix='/tasks')

# Helper function to filter tasks by date range in user's timezone
def get_tasks_in_range(user_id, start_date, end_date):
    tasks = Task.query.filter(Task.user_id == user_id, Task.start_time >= start_date, Task.end_time <= end_date) \
        .order_by(Task.start_time.asc()).all()  # Sort by start_time ascending
    return jsonify([task.to_dict() for task in tasks])


# Route to get all tasks or filter by date range (with timezone handling)
@bp.route('/', methods=['GET'])
@jwt_required()
def get_tasks():
    user_id = get_jwt_identity()
    start_time = request.args.get('start_time')  # Optional 'start_time' query parameter
    end_time = request.args.get('end_time')  # Optional 'end_time' query parameter

    # Retrieve the user's timezone
    user = User.query.get(user_id)
    user_timezone = pytz.timezone(user.timezone)

    # Define UTC timezone
    utc = pytz.utc

    # If both start_time and end_time are provided, filter by the date range
    if start_time and end_time:
        try:
            # Convert start_time and end_time from string to datetime in user's timezone
            start_time = datetime.strptime(start_time, '%Y-%m-%d %H:%M:%S')
            end_time = datetime.strptime(end_time, '%Y-%m-%d %H:%M:%S')

            # Localize the times to the user's timezone, then convert to UTC
            start_time = user_timezone.localize(start_time).astimezone(utc)
            end_time = user_timezone.localize(end_time).astimezone(utc)

        except ValueError:
            return jsonify({'error': 'Invalid datetime format. Use YYYY-MM-DD HH:MM:SS'}), 400

        tasks = Task.query.filter(Task.user_id == user_id, Task.start_time >= start_time, Task.end_time <= end_time) \
            .order_by(Task.start_time.asc()).all()
    else:
        # If no start_time and end_time are provided, get all tasks
        tasks = Task.query.filter_by(user_id=user_id).order_by(Task.start_time.asc()).all()

    return jsonify([task.to_dict() for task in tasks])


# Get tasks for a specific day or today if not provided (with timezone handling)
@bp.route('/daily', methods=['GET'])
@jwt_required()
def get_daily_tasks():
    user_id = get_jwt_identity()
    date_param = request.args.get('date')  # Optional query parameter: 'YYYY-MM-DD'

    # Retrieve the user's timezone
    user = User.query.get(user_id)
    user_timezone = pytz.timezone(user.timezone)

    if date_param:
        day = datetime.strptime(date_param, '%Y-%m-%d').date()
    else:
        day = datetime.utcnow().date()

    # Localize to the user's timezone and convert to UTC
    start_of_day = user_timezone.localize(datetime.combine(day, datetime.min.time())).astimezone(pytz.utc)
    end_of_day = user_timezone.localize(datetime.combine(day, datetime.max.time())).astimezone(pytz.utc)

    return get_tasks_in_range(user_id, start_of_day, end_of_day)


# Get tasks for a specific week or this week if not provided (with timezone handling)
@bp.route('/weekly', methods=['GET'])
@jwt_required()
def get_weekly_tasks():
    user_id = get_jwt_identity()
    date_param = request.args.get('date')  # Optional query parameter: 'YYYY-MM-DD'

    # Retrieve the user's timezone
    user = User.query.get(user_id)
    user_timezone = pytz.timezone(user.timezone)

    if date_param:
        day = datetime.strptime(date_param, '%Y-%m-%d').date()
    else:
        day = datetime.utcnow().date()

    # Calculate the start and end of the week
    start_of_week = day - timedelta(days=day.weekday())  # Start of the week (Monday)
    end_of_week = start_of_week + timedelta(days=6)  # End of the week (Sunday)

    # Convert start and end of the week to user's timezone and then UTC
    start_of_week = user_timezone.localize(datetime.combine(start_of_week, datetime.min.time())).astimezone(pytz.utc)
    end_of_week = user_timezone.localize(datetime.combine(end_of_week, datetime.max.time())).astimezone(pytz.utc)

    return get_tasks_in_range(user_id, start_of_week, end_of_week)


# Get tasks for a specific month or this month if not provided (with timezone handling)
@bp.route('/monthly', methods=['GET'])
@jwt_required()
def get_monthly_tasks():
    user_id = get_jwt_identity()
    date_param = request.args.get('date')  # Optional query parameter: 'YYYY-MM'

    # Retrieve the user's timezone
    user = User.query.get(user_id)
    user_timezone = pytz.timezone(user.timezone)

    if date_param:
        day = datetime.strptime(date_param, '%Y-%m').date()
    else:
        day = datetime.utcnow().date()

    # Calculate the start and end of the month
    start_of_month = day.replace(day=1)
    _, last_day = calendar.monthrange(day.year, day.month)
    end_of_month = day.replace(day=last_day)

    # Convert start and end of the month to user's timezone and then UTC
    start_of_month = user_timezone.localize(datetime.combine(start_of_month, datetime.min.time())).astimezone(pytz.utc)
    end_of_month = user_timezone.localize(datetime.combine(end_of_month, datetime.max.time())).astimezone(pytz.utc)

    return get_tasks_in_range(user_id, start_of_month, end_of_month)


# Create a task with timezone handling
@bp.route('/', methods=['POST'])
@jwt_required()
def create_task():
    data = request.get_json()
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    user_timezone = pytz.timezone(user.timezone)

    # Convert start_time and end_time to user's timezone and then UTC
    start_time = datetime.strptime(data['start_time'],
                                   '%Y-%m-%d %H:%M:%S') if 'start_time' in data else datetime.utcnow()
    start_time = user_timezone.localize(start_time).astimezone(pytz.utc)

    end_time = datetime.strptime(data['end_time'], '%Y-%m-%d %H:%M:%S') if 'end_time' in data else None
    if end_time:
        end_time = user_timezone.localize(end_time).astimezone(pytz.utc)

    task = Task(
        title=data['title'],
        user_id=user_id,
        start_time=start_time,
        end_time=end_time
    )
    db.session.add(task)
    db.session.commit()

    return jsonify({'message': 'Task created successfully'}), 201


# Update a task (optional, timezone conversion if needed)
@bp.route('/<string:id>', methods=['PUT'])
@jwt_required()
def update_task(id):
    task = Task.query.get_or_404(id)
    data = request.get_json()
    task.title = data['title']
    db.session.commit()
    return jsonify({'message': 'Task updated successfully'})


# Delete a task
@bp.route('/<string:id>', methods=['DELETE'])
@jwt_required()
def delete_task(id):
    task = Task.query.get_or_404(id)
    db.session.delete(task)
    db.session.commit()
    return jsonify({'message': 'Task deleted successfully'})
