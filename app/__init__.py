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

    # Dodaj zaglavlja da onemogućiš keširanje za svaki odgovor.
    @app.after_request
    def add_header(response):
        response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '-1'
        return response

    # Registruj seed komandu
    @app.cli.command("seed")
    def seed():
        # Proveri da li su User i Task tabele prazne
        if not User.query.first() and not Task.query.first():
            users_data = [
                {
                    "username": "vasilije",
                    "password": "vasilije",
                },
                {
                    "username": "marija",
                    "password": "marija",
                },
                {
                    "username": "pedja",
                    "password": "pedja",
                }
            ]

            # Kreiraj i ubaci korisnike
            users = []
            for user_data in users_data:
                user = User(
                    username=user_data["username"],
                    password=user_data["password"],
                )
                users.append(user)

            db.session.add_all(users)
            db.session.commit()

            # Preuzmi kreirane korisnike iz baze (jer su nam potrebni njihovi ID-jevi)
            users_in_db = User.query.all()

            # Unapred definisani podaci
            tasks_data = [
                {
                    "title": "Završavanje projektnog izveštaja",
                    "body": "Završiti godišnji projektni izveštaj i predati ga.",
                    "tag": "posao",
                    "start_time": datetime(2024, 8, 1, 9, 0),
                    "end_time": datetime(2024, 8, 1, 12, 0),
                    "user_id": users_in_db[0].id  # Dodeli za john_doe
                },
                {
                    "title": "Tim sastanak",
                    "body": "Mesečni sastanak tima.",
                    "tag": "sastanak",
                    "start_time": datetime(2024, 8, 2, 14, 0),
                    "end_time": datetime(2024, 8, 2, 15, 0),
                    "user_id": users_in_db[0].id  # Dodeli za john_doe
                },
                {
                    "title": "Poziv sa klijentom",
                    "body": "Poziv sa klijentom radi diskusije o napretku projekta.",
                    "tag": "klijent",
                    "start_time": datetime(2024, 8, 3, 11, 0),
                    "end_time": datetime(2024, 8, 3, 12, 0),
                    "user_id": users_in_db[1].id  # Dodeli za jane_smith
                },
                {
                    "title": "Pregled PR-ova",
                    "body": "Pregled najnovijih zahteva za pridruživanje koda od tima.",
                    "tag": "posao",
                    "start_time": datetime(2024, 8, 4, 16, 0),
                    "end_time": datetime(2024, 8, 4, 18, 0),
                    "user_id": users_in_db[1].id  # Dodeli za jane_smith
                },
                {
                    "title": "Završavanje dokumentacije",
                    "body": "Kompletiranje dokumentacije projekta.",
                    "tag": "dokumentacija",
                    "start_time": datetime(2024, 8, 5, 10, 0),
                    "end_time": datetime(2024, 8, 5, 13, 0),
                    "user_id": users_in_db[2].id  # Dodeli za alice_wonder
                }
            ]

            # Konvertuj zadatke u UTC radi skladištenja
            tasks_to_be_inserted = []
            for task_data in tasks_data:
                task = Task(
                    title=task_data["title"],
                    body=task_data["body"],
                    tag=task_data["tag"],
                    start_time=task_data["start_time"],
                    end_time=task_data["end_time"],
                    user_id=task_data["user_id"]
                )
                tasks_to_be_inserted.append(task)

            db.session.add_all(tasks_to_be_inserted)
            db.session.commit()

            print("Seeding completed successfully.")  # Uspešno završen seeding
        else:
            print("Tables are not empty, skipping seed.")  # Tabele nisu prazne, preskačem seeding

    return app
