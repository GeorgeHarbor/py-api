from flask import Flask
from .extensions import db, jwt, migrate
from .api import auth, tasks

def create_app():
    app = Flask(__name__)

    app.config.from_object('app.config.Config')

    db.init_app(app)
    jwt.init_app(app)
    migrate.init_app(app, db)


    app.register_blueprint(auth.bp)
    app.register_blueprint(tasks.bp)

    return app
