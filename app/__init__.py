from datetime import datetime
import pytz
from flask import Flask
from .extensions import db, jwt, migrate
from .api import auth, tasks
from .models import User, Task

def create_app():
    app = Flask(__name__)

    app.config.from_object('app.config.Config')

    db.init_app(app)
    jwt.init_app(app)
    migrate.init_app(app, db)

    app.register_blueprint(auth.bp)
    app.register_blueprint(tasks.bp)



    @app.after_request
    def add_header(response):
        """
        Add headers to disable caching for every response.
        """
        response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '-1'
        return response


    # Register the seed command
    @app.cli.command("seed")
    def seed():
        # Check if User and Task tables are empty
        if not User.query.first() and not Task.query.first():
            print("Seeding hardcoded data with Europe/Belgrade timezone...")

            # Belgrade timezone
            belgrade_tz = pytz.timezone('Europe/Belgrade')

            # Hardcoded users data with Europe/Belgrade timezone
            users_data = [
                {
                    "username": "john_doe",
                    "password": "password123",
                    "timezone": "Europe/Belgrade"
                },
                {
                    "username": "jane_smith",
                    "password": "password123",
                    "timezone": "Europe/Belgrade"
                },
                {
                    "username": "alice_wonder",
                    "password": "password123",
                    "timezone": "Europe/Belgrade"
                }
            ]

            # Create and insert users
            users = []
            for user_data in users_data:
                user = User(
                    username=user_data["username"],
                    timezone=user_data["timezone"]
                )
                user.set_password(user_data["password"])
                users.append(user)

            db.session.add_all(users)
            db.session.commit()

            # Get the created users from the database (since we need their IDs)
            users_in_db = User.query.all()

            # Hardcoded tasks data in Europe/Belgrade timezone with body and tag
            tasks_data = [
                {
                    "title": "Complete project report",
                    "body": "Finish the annual project report and submit it.",
                    "tag": "work",
                    "start_time": belgrade_tz.localize(datetime(2024, 8, 1, 9, 0)),  # Belgrade time
                    "end_time": belgrade_tz.localize(datetime(2024, 8, 1, 12, 0)),  # Belgrade time
                    "user_id": users_in_db[0].id  # Assign to john_doe
                },
                {
                    "title": "Team meeting",
                    "body": "Monthly team sync-up meeting.",
                    "tag": "meeting",
                    "start_time": belgrade_tz.localize(datetime(2024, 8, 2, 14, 0)),  # Belgrade time
                    "end_time": belgrade_tz.localize(datetime(2024, 8, 2, 15, 0)),  # Belgrade time
                    "user_id": users_in_db[0].id  # Assign to john_doe
                },
                {
                    "title": "Client call",
                    "body": "Call with the client to discuss project progress.",
                    "tag": "client",
                    "start_time": belgrade_tz.localize(datetime(2024, 8, 3, 11, 0)),  # Belgrade time
                    "end_time": belgrade_tz.localize(datetime(2024, 8, 3, 12, 0)),  # Belgrade time
                    "user_id": users_in_db[1].id  # Assign to jane_smith
                },
                {
                    "title": "Review PRs",
                    "body": "Review the latest pull requests from the team.",
                    "tag": "work",
                    "start_time": belgrade_tz.localize(datetime(2024, 8, 4, 16, 0)),  # Belgrade time
                    "end_time": belgrade_tz.localize(datetime(2024, 8, 4, 18, 0)),  # Belgrade time
                    "user_id": users_in_db[1].id  # Assign to jane_smith
                },
                {
                    "title": "Finish documentation",
                    "body": "Complete the project documentation.",
                    "tag": "documentation",
                    "start_time": belgrade_tz.localize(datetime(2024, 8, 5, 10, 0)),  # Belgrade time
                    "end_time": belgrade_tz.localize(datetime(2024, 8, 5, 13, 0)),  # Belgrade time
                    "user_id": users_in_db[2].id  # Assign to alice_wonder
                }
            ]

            # Convert tasks to UTC for storage
            tasks_to_be_inserted = []
            for task_data in tasks_data:
                task = Task(
                    title=task_data["title"],
                    body=task_data["body"],
                    tag=task_data["tag"],
                    start_time=task_data["start_time"].astimezone(pytz.utc),  # Convert to UTC for storage
                    end_time=task_data["end_time"].astimezone(pytz.utc),  # Convert to UTC for storage
                    user_id=task_data["user_id"]
                )
                tasks_to_be_inserted.append(task)

            db.session.add_all(tasks_to_be_inserted)
            db.session.commit()

            print("Seeding completed successfully.")
        else:
            print("Tables are not empty, skipping seed.")

    return app
